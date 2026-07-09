import 'availability_slot.dart';
import 'barber_summary.dart';

class AvailabilityData {
  const AvailabilityData({
    required this.serviceId,
    required this.date,
    required this.barbers,
    required this.slots,
  });

  final String serviceId;
  final DateTime date;
  final List<BarberSummary> barbers;
  final List<AvailabilitySlot> slots;
}
