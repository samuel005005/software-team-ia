import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../services/domain/entities/service_item.dart';
import '../../../../core/providers/network_providers.dart';
import '../../data/datasources/appointments_remote_data_source.dart';
import '../../data/datasources/availability_remote_data_source.dart';
import '../../data/datasources/barbers_remote_data_source.dart';
import '../../data/repositories/booking_repository_impl.dart';
import '../../domain/entities/availability_data.dart';
import '../../domain/entities/availability_slot.dart';
import '../../domain/entities/barber_summary.dart';
import '../../domain/entities/booked_appointment.dart';
import '../../domain/repositories/booking_repository.dart';
import '../../domain/usecases/create_appointment_use_case.dart';
import '../../domain/usecases/get_availability_use_case.dart';
import '../../domain/usecases/list_barbers_for_service_use_case.dart';

final barbersRemoteDataSourceProvider = Provider<BarbersRemoteDataSource>((ref) {
  return BarbersRemoteDataSource(ref.watch(dioProvider));
});

final availabilityRemoteDataSourceProvider =
    Provider<AvailabilityRemoteDataSource>((ref) {
  return AvailabilityRemoteDataSource(ref.watch(dioProvider));
});

final appointmentsRemoteDataSourceProvider =
    Provider<AppointmentsRemoteDataSource>((ref) {
  return AppointmentsRemoteDataSource(ref.watch(dioProvider));
});

final bookingRepositoryProvider = Provider<BookingRepository>((ref) {
  return BookingRepositoryImpl(
    barbersRemote: ref.watch(barbersRemoteDataSourceProvider),
    availabilityRemote: ref.watch(availabilityRemoteDataSourceProvider),
    appointmentsRemote: ref.watch(appointmentsRemoteDataSourceProvider),
  );
});

final listBarbersForServiceUseCaseProvider =
    Provider<ListBarbersForServiceUseCase>((ref) {
  return ListBarbersForServiceUseCase(ref.watch(bookingRepositoryProvider));
});

final getAvailabilityUseCaseProvider = Provider<GetAvailabilityUseCase>((ref) {
  return GetAvailabilityUseCase(ref.watch(bookingRepositoryProvider));
});

final createAppointmentUseCaseProvider =
    Provider<CreateAppointmentUseCase>((ref) {
  return CreateAppointmentUseCase(ref.watch(bookingRepositoryProvider));
});

final barbersForServiceProvider =
    FutureProvider.autoDispose.family<List<BarberSummary>, String>(
  (ref, serviceId) async {
    final result = await ref
        .watch(listBarbersForServiceUseCaseProvider)
        .call(ListBarbersForServiceParams(serviceId));
    return result.when(
      success: (barbers) => barbers,
      error: (failure) => throw failure,
    );
  },
);

class AvailabilityQuery {
  const AvailabilityQuery({
    required this.serviceId,
    required this.date,
    this.barberId,
  });

  final String serviceId;
  final DateTime date;
  final String? barberId;

  @override
  bool operator ==(Object other) {
    return other is AvailabilityQuery &&
        other.serviceId == serviceId &&
        other.date.year == date.year &&
        other.date.month == date.month &&
        other.date.day == date.day &&
        other.barberId == barberId;
  }

  @override
  int get hashCode => Object.hash(
        serviceId,
        date.year,
        date.month,
        date.day,
        barberId,
      );
}

final availabilityProvider =
    FutureProvider.autoDispose.family<AvailabilityData, AvailabilityQuery>(
  (ref, query) async {
    final result = await ref.watch(getAvailabilityUseCaseProvider).call(
          GetAvailabilityParams(
            serviceId: query.serviceId,
            date: query.date,
            barberId: query.barberId,
          ),
        );
    return result.when(
      success: (data) => data,
      error: (failure) => throw failure,
    );
  },
);

class BookingWizardState {
  const BookingWizardState({
    this.currentStep = 0,
    this.service,
    this.barber,
    this.selectedDate,
    this.selectedSlot,
    this.isSubmitting = false,
    this.confirmedAppointment,
  });

  final int currentStep;
  final ServiceItem? service;
  final BarberSummary? barber;
  final DateTime? selectedDate;
  final AvailabilitySlot? selectedSlot;
  final bool isSubmitting;
  final BookedAppointment? confirmedAppointment;

  bool get isConfirmed => confirmedAppointment != null;

  bool get canAdvance {
    switch (currentStep) {
      case 0:
        return service != null;
      case 1:
        return barber != null;
      case 2:
        return selectedSlot != null;
      case 3:
        return true;
      default:
        return false;
    }
  }

  BookingWizardState copyWith({
    int? currentStep,
    ServiceItem? service,
    bool clearService = false,
    BarberSummary? barber,
    bool clearBarber = false,
    DateTime? selectedDate,
    bool clearSelectedDate = false,
    AvailabilitySlot? selectedSlot,
    bool clearSelectedSlot = false,
    bool? isSubmitting,
    BookedAppointment? confirmedAppointment,
    bool clearConfirmedAppointment = false,
  }) {
    return BookingWizardState(
      currentStep: currentStep ?? this.currentStep,
      service: clearService ? null : (service ?? this.service),
      barber: clearBarber ? null : (barber ?? this.barber),
      selectedDate:
          clearSelectedDate ? null : (selectedDate ?? this.selectedDate),
      selectedSlot:
          clearSelectedSlot ? null : (selectedSlot ?? this.selectedSlot),
      isSubmitting: isSubmitting ?? this.isSubmitting,
      confirmedAppointment: clearConfirmedAppointment
          ? null
          : (confirmedAppointment ?? this.confirmedAppointment),
    );
  }
}

class BookingWizardNotifier extends StateNotifier<BookingWizardState> {
  BookingWizardNotifier() : super(const BookingWizardState());

  void selectService(ServiceItem service) {
    state = state.copyWith(
      service: service,
      clearBarber: true,
      clearSelectedDate: true,
      clearSelectedSlot: true,
    );
  }

  void selectBarber(BarberSummary barber) {
    state = state.copyWith(
      barber: barber,
      clearSelectedDate: true,
      clearSelectedSlot: true,
    );
  }

  void selectDate(DateTime date) {
    state = state.copyWith(
      selectedDate: DateTime(date.year, date.month, date.day),
      clearSelectedSlot: true,
    );
  }

  void selectSlot(AvailabilitySlot slot) {
    state = state.copyWith(selectedSlot: slot);
  }

  void goToStep(int step) {
    state = state.copyWith(currentStep: step);
  }

  void nextStep() {
    if (!state.canAdvance || state.currentStep >= 3) return;
    state = state.copyWith(currentStep: state.currentStep + 1);
  }

  void previousStep() {
    if (state.currentStep <= 0) return;
    state = state.copyWith(currentStep: state.currentStep - 1);
  }

  void setSubmitting(bool value) {
    state = state.copyWith(isSubmitting: value);
  }

  void confirmAppointment(BookedAppointment appointment) {
    state = state.copyWith(
      confirmedAppointment: appointment,
      isSubmitting: false,
    );
  }

  void handleSlotConflict() {
    state = state.copyWith(
      currentStep: 2,
      clearSelectedSlot: true,
      isSubmitting: false,
    );
  }

  void reset() {
    state = const BookingWizardState();
  }
}

final bookingWizardProvider =
    StateNotifierProvider<BookingWizardNotifier, BookingWizardState>((ref) {
  return BookingWizardNotifier();
});
