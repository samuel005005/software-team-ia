import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../../app/router/routes.dart';
import '../../../../core/error/failures.dart';
import '../../../services/domain/entities/service_item.dart';
import '../../../services/presentation/providers/services_providers.dart';
import '../../domain/entities/availability_slot.dart';
import '../../domain/entities/barber_summary.dart';
import '../../domain/entities/booked_appointment.dart';
import '../../domain/usecases/create_appointment_use_case.dart';
import '../providers/booking_providers.dart';

class BookAppointmentPage extends ConsumerStatefulWidget {
  const BookAppointmentPage({super.key, this.initialServiceId});

  final String? initialServiceId;

  @override
  ConsumerState<BookAppointmentPage> createState() =>
      _BookAppointmentPageState();
}

class _BookAppointmentPageState extends ConsumerState<BookAppointmentPage> {
  bool _initialServiceApplied = false;

  @override
  void initState() {
    super.initState();
    if (widget.initialServiceId != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _applyInitialServiceIfNeeded();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final wizard = ref.watch(bookingWizardProvider);

    ref.listen(activeServicesProvider, (previous, next) {
      next.whenData(_applyInitialServiceFromList);
    });

    if (wizard.isConfirmed) {
      return _BookingConfirmationView(
        appointment: wizard.confirmedAppointment!,
        onBookAnother: () => ref.read(bookingWizardProvider.notifier).reset(),
        onViewAppointments: () => context.go(AppRoutes.appointments),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Reservar cita'),
      ),
      body: Column(
        children: [
          Expanded(
            child: Stepper(
              currentStep: wizard.currentStep,
              onStepTapped: (step) {
                if (step < wizard.currentStep) {
                  ref.read(bookingWizardProvider.notifier).goToStep(step);
                }
              },
              controlsBuilder: (context, details) => const SizedBox.shrink(),
              steps: [
                Step(
                  title: const Text('Servicio'),
                  isActive: wizard.currentStep >= 0,
                  state: _stepState(wizard.currentStep, 0, wizard.service != null),
                  content: _BookingStepService(
                    selectedService: wizard.service,
                    onServiceSelected: (service) {
                      ref
                          .read(bookingWizardProvider.notifier)
                          .selectService(service);
                    },
                  ),
                ),
                Step(
                  title: const Text('Barbero'),
                  isActive: wizard.currentStep >= 1,
                  state: _stepState(wizard.currentStep, 1, wizard.barber != null),
                  content: wizard.service == null
                      ? const Text('Selecciona un servicio primero.')
                      : _BookingStepBarber(
                          serviceId: wizard.service!.id,
                          selectedBarber: wizard.barber,
                          onBarberSelected: (barber) {
                            ref
                                .read(bookingWizardProvider.notifier)
                                .selectBarber(barber);
                          },
                        ),
                ),
                Step(
                  title: const Text('Fecha y hora'),
                  isActive: wizard.currentStep >= 2,
                  state: _stepState(
                    wizard.currentStep,
                    2,
                    wizard.selectedSlot != null,
                  ),
                  content: wizard.service == null || wizard.barber == null
                      ? const Text('Selecciona servicio y barbero primero.')
                      : _BookingStepDateTime(
                          serviceId: wizard.service!.id,
                          barber: wizard.barber!,
                          selectedDate: wizard.selectedDate,
                          selectedSlot: wizard.selectedSlot,
                          onDateSelected: (date) {
                            ref
                                .read(bookingWizardProvider.notifier)
                                .selectDate(date);
                          },
                          onSlotSelected: (slot) {
                            ref
                                .read(bookingWizardProvider.notifier)
                                .selectSlot(slot);
                          },
                        ),
                ),
                Step(
                  title: const Text('Confirmar'),
                  isActive: wizard.currentStep >= 3,
                  state: _stepState(wizard.currentStep, 3, true),
                  content: wizard.service == null ||
                          wizard.barber == null ||
                          wizard.selectedSlot == null
                      ? const Text('Completa los pasos anteriores.')
                      : _BookingStepConfirm(
                          service: wizard.service!,
                          barber: wizard.barber!,
                          slot: wizard.selectedSlot!,
                          isSubmitting: wizard.isSubmitting,
                          onConfirm: () => _submitBooking(),
                        ),
                ),
              ],
            ),
          ),
          _BookingNavigationBar(
            currentStep: wizard.currentStep,
            canAdvance: wizard.canAdvance,
            isSubmitting: wizard.isSubmitting,
            onBack: () =>
                ref.read(bookingWizardProvider.notifier).previousStep(),
            onNext: () => ref.read(bookingWizardProvider.notifier).nextStep(),
          ),
        ],
      ),
    );
  }

  void _applyInitialServiceFromList(List<ServiceItem> services) {
    if (_initialServiceApplied || widget.initialServiceId == null) return;

    ServiceItem? match;
    for (final service in services) {
      if (service.id == widget.initialServiceId) {
        match = service;
        break;
      }
    }
    if (match != null) {
      _initialServiceApplied = true;
      ref.read(bookingWizardProvider.notifier).selectService(match);
      ref.read(bookingWizardProvider.notifier).goToStep(1);
    }
  }

  void _applyInitialServiceIfNeeded() {
    if (_initialServiceApplied || widget.initialServiceId == null) return;

    final servicesAsync = ref.read(activeServicesProvider);
    servicesAsync.when(
      data: _applyInitialServiceFromList,
      loading: () {},
      error: (_, __) {},
    );
  }

  Future<void> _submitBooking() async {
    final wizard = ref.read(bookingWizardProvider);
    final service = wizard.service;
    final barber = wizard.barber;
    final slot = wizard.selectedSlot;

    if (service == null || barber == null || slot == null) return;

    ref.read(bookingWizardProvider.notifier).setSubmitting(true);

    final result = await ref.read(createAppointmentUseCaseProvider).call(
          CreateAppointmentParams(
            barberUserId: barber.userId,
            serviceId: service.id,
            scheduledStartIso: slot.startIso,
          ),
        );

    if (!mounted) return;

    result.when(
      success: (appointment) {
        ref.read(bookingWizardProvider.notifier).confirmAppointment(appointment);
      },
      error: (failure) {
        ref.read(bookingWizardProvider.notifier).setSubmitting(false);

        final message = failure.message;
        final isSlotConflict = failure is ValidationFailure &&
            message.toLowerCase().contains('disponible');

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );

        if (isSlotConflict) {
          final query = AvailabilityQuery(
            serviceId: service.id,
            date: wizard.selectedDate ?? slot.start,
            barberId: barber.userId,
          );
          ref.invalidate(availabilityProvider(query));
          ref.read(bookingWizardProvider.notifier).handleSlotConflict();
        }
      },
    );
  }

  StepState _stepState(int current, int step, bool completed) {
    if (current > step || (current == step && completed && current < 3)) {
      return StepState.complete;
    }
    if (current == step) return StepState.editing;
    return StepState.indexed;
  }
}

class _BookingNavigationBar extends StatelessWidget {
  const _BookingNavigationBar({
    required this.currentStep,
    required this.canAdvance,
    required this.isSubmitting,
    required this.onBack,
    required this.onNext,
  });

  final int currentStep;
  final bool canAdvance;
  final bool isSubmitting;
  final VoidCallback onBack;
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            if (currentStep > 0)
              OutlinedButton(
                onPressed: isSubmitting ? null : onBack,
                child: const Text('Atrás'),
              ),
            const Spacer(),
            if (currentStep < 3)
              FilledButton(
                onPressed: canAdvance && !isSubmitting ? onNext : null,
                child: const Text('Siguiente'),
              ),
          ],
        ),
      ),
    );
  }
}

class _BookingStepService extends ConsumerWidget {
  const _BookingStepService({
    required this.selectedService,
    required this.onServiceSelected,
  });

  final ServiceItem? selectedService;
  final ValueChanged<ServiceItem> onServiceSelected;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final servicesAsync = ref.watch(activeServicesProvider);

    return servicesAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(error.toString()),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () => ref.invalidate(activeServicesProvider),
            child: const Text('Reintentar'),
          ),
        ],
      ),
      data: (services) {
        if (services.isEmpty) {
          return const Text('No hay servicios disponibles por ahora.');
        }

        return Column(
          children: services
              .map(
                (service) {
                  final isSelected = selectedService?.id == service.id;
                  return Card(
                    color: isSelected
                        ? Theme.of(context).colorScheme.primaryContainer
                        : null,
                    child: ListTile(
                      title: Text(service.name),
                      subtitle: Text(
                        '${service.durationMinutes} min · RD\$${service.priceDop}',
                      ),
                      trailing: isSelected
                          ? Icon(
                              Icons.check_circle,
                              color: Theme.of(context).colorScheme.primary,
                            )
                          : null,
                      onTap: () => onServiceSelected(service),
                    ),
                  );
                },
              )
              .toList(),
        );
      },
    );
  }
}

class _BookingStepBarber extends ConsumerWidget {
  const _BookingStepBarber({
    required this.serviceId,
    required this.selectedBarber,
    required this.onBarberSelected,
  });

  final String serviceId;
  final BarberSummary? selectedBarber;
  final ValueChanged<BarberSummary> onBarberSelected;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final barbersAsync = ref.watch(barbersForServiceProvider(serviceId));

    return barbersAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(error.toString()),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () =>
                ref.invalidate(barbersForServiceProvider(serviceId)),
            child: const Text('Reintentar'),
          ),
        ],
      ),
      data: (barbers) {
        if (barbers.isEmpty) {
          return const Text(
            'No hay barberos disponibles para este servicio.',
          );
        }

        return Column(
          children: barbers
              .map(
                (barber) {
                  final isSelected = selectedBarber?.userId == barber.userId;
                  return Card(
                    color: isSelected
                        ? Theme.of(context).colorScheme.primaryContainer
                        : null,
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundImage: barber.photoUrl != null
                            ? NetworkImage(barber.photoUrl!)
                            : null,
                        child: barber.photoUrl == null
                            ? Text(
                                barber.displayName.isNotEmpty
                                    ? barber.displayName[0].toUpperCase()
                                    : '?',
                              )
                            : null,
                      ),
                      title: Text(barber.displayName),
                      subtitle: barber.bio != null && barber.bio!.isNotEmpty
                          ? Text(
                              barber.bio!,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            )
                          : null,
                      trailing: isSelected
                          ? Icon(
                              Icons.check_circle,
                              color: Theme.of(context).colorScheme.primary,
                            )
                          : null,
                      onTap: () => onBarberSelected(barber),
                    ),
                  );
                },
              )
              .toList(),
        );
      },
    );
  }
}

class _BookingStepDateTime extends ConsumerWidget {
  const _BookingStepDateTime({
    required this.serviceId,
    required this.barber,
    required this.selectedDate,
    required this.selectedSlot,
    required this.onDateSelected,
    required this.onSlotSelected,
  });

  final String serviceId;
  final BarberSummary barber;
  final DateTime? selectedDate;
  final AvailabilitySlot? selectedSlot;
  final ValueChanged<DateTime> onDateSelected;
  final ValueChanged<AvailabilitySlot> onSlotSelected;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat.yMMMd('es');
    final timeFormat = DateFormat.Hm('es');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        FilledButton.tonal(
          onPressed: () => _pickDate(context),
          child: Text(
            selectedDate == null
                ? 'Elegir fecha'
                : 'Fecha: ${dateFormat.format(selectedDate!)}',
          ),
        ),
        const SizedBox(height: 16),
        if (selectedDate != null) ...[
          Text(
            'Horarios de ${barber.displayName}',
            style: theme.textTheme.titleSmall,
          ),
          const SizedBox(height: 8),
          _AvailabilitySlots(
            serviceId: serviceId,
            barberId: barber.userId,
            date: selectedDate!,
            selectedSlot: selectedSlot,
            timeFormat: timeFormat,
            onSlotSelected: onSlotSelected,
          ),
        ],
      ],
    );
  }

  Future<void> _pickDate(BuildContext context) async {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final picked = await showDatePicker(
      context: context,
      initialDate: selectedDate ?? today,
      firstDate: today,
      lastDate: today.add(const Duration(days: 90)),
      locale: const Locale('es'),
    );
    if (picked != null) onDateSelected(picked);
  }
}

class _AvailabilitySlots extends ConsumerWidget {
  const _AvailabilitySlots({
    required this.serviceId,
    required this.barberId,
    required this.date,
    required this.selectedSlot,
    required this.timeFormat,
    required this.onSlotSelected,
  });

  final String serviceId;
  final String barberId;
  final DateTime date;
  final AvailabilitySlot? selectedSlot;
  final DateFormat timeFormat;
  final ValueChanged<AvailabilitySlot> onSlotSelected;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final query = AvailabilityQuery(
      serviceId: serviceId,
      date: date,
      barberId: barberId,
    );
    final availabilityAsync = ref.watch(availabilityProvider(query));

    return availabilityAsync.when(
      loading: () => const Padding(
        padding: EdgeInsets.symmetric(vertical: 16),
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (error, _) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(error.toString()),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () => ref.invalidate(availabilityProvider(query)),
            child: const Text('Reintentar'),
          ),
        ],
      ),
      data: (availability) {
        final slots = availability.slots
            .where((slot) => slot.barberUserId == barberId)
            .toList();

        if (slots.isEmpty) {
          return const Text(
            'No hay horarios disponibles para esta fecha. Prueba otra fecha.',
          );
        }

        return Wrap(
          spacing: 8,
          runSpacing: 8,
          children: slots.map((slot) {
            final isSelected = selectedSlot != null &&
                selectedSlot!.start == slot.start &&
                selectedSlot!.barberUserId == slot.barberUserId;
            return ChoiceChip(
              label: Text(timeFormat.format(slot.start)),
              selected: isSelected,
              onSelected: (_) => onSlotSelected(slot),
            );
          }).toList(),
        );
      },
    );
  }
}

class _BookingStepConfirm extends StatelessWidget {
  const _BookingStepConfirm({
    required this.service,
    required this.barber,
    required this.slot,
    required this.isSubmitting,
    required this.onConfirm,
  });

  final ServiceItem service;
  final BarberSummary barber;
  final AvailabilitySlot slot;
  final bool isSubmitting;
  final VoidCallback onConfirm;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat.yMMMEd('es');
    final timeFormat = DateFormat.Hm('es');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Resumen de tu cita', style: theme.textTheme.titleMedium),
        const SizedBox(height: 12),
        _SummaryRow(label: 'Servicio', value: service.name),
        _SummaryRow(label: 'Barbero', value: barber.displayName),
        _SummaryRow(label: 'Fecha', value: dateFormat.format(slot.start)),
        _SummaryRow(
          label: 'Hora',
          value:
              '${timeFormat.format(slot.start)} – ${timeFormat.format(slot.end)}',
        ),
        _SummaryRow(
          label: 'Duración',
          value: '${service.durationMinutes} min',
        ),
        _SummaryRow(label: 'Precio', value: 'RD\$${service.priceDop}'),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: isSubmitting ? null : onConfirm,
          child: isSubmitting
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Confirmar reserva'),
        ),
      ],
    );
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 88,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

class _BookingConfirmationView extends StatelessWidget {
  const _BookingConfirmationView({
    required this.appointment,
    required this.onBookAnother,
    required this.onViewAppointments,
  });

  final BookedAppointment appointment;
  final VoidCallback onBookAnother;
  final VoidCallback onViewAppointments;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat.yMMMEd('es');
    final timeFormat = DateFormat.Hm('es');

    return Scaffold(
      appBar: AppBar(title: const Text('Cita confirmada')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Icon(
              Icons.check_circle_outline,
              size: 72,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(height: 16),
            Text(
              '¡Tu cita está confirmada!',
              style: theme.textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _SummaryRow(
                      label: 'Estado',
                      value: appointment.status,
                    ),
                    _SummaryRow(
                      label: 'Servicio',
                      value: appointment.serviceName,
                    ),
                    _SummaryRow(
                      label: 'Barbero',
                      value: appointment.barberDisplayName,
                    ),
                    _SummaryRow(
                      label: 'Fecha',
                      value: dateFormat.format(appointment.scheduledStart),
                    ),
                    _SummaryRow(
                      label: 'Hora',
                      value:
                          '${timeFormat.format(appointment.scheduledStart)} – ${timeFormat.format(appointment.scheduledEnd)}',
                    ),
                  ],
                ),
              ),
            ),
            const Spacer(),
            FilledButton(
              onPressed: onViewAppointments,
              child: const Text('Ver mis citas'),
            ),
            const SizedBox(height: 8),
            OutlinedButton(
              onPressed: onBookAnother,
              child: const Text('Reservar otra'),
            ),
          ],
        ),
      ),
    );
  }
}
