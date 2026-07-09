class AvailabilityDay {
  const AvailabilityDay({
    required this.weekday,
    required this.startTime,
    required this.endTime,
    required this.isActive,
  });

  final int weekday;
  final String startTime;
  final String endTime;
  final bool isActive;

  AvailabilityDay copyWith({
    int? weekday,
    String? startTime,
    String? endTime,
    bool? isActive,
  }) {
    return AvailabilityDay(
      weekday: weekday ?? this.weekday,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      isActive: isActive ?? this.isActive,
    );
  }

  static List<AvailabilityDay> defaultWeek() {
    return List.generate(
      7,
      (index) => AvailabilityDay(
        weekday: index + 1,
        startTime: '09:00:00',
        endTime: '18:00:00',
        isActive: false,
      ),
    );
  }

  static String weekdayLabel(int weekday) {
    switch (weekday) {
      case 1:
        return 'Lunes';
      case 2:
        return 'Martes';
      case 3:
        return 'Miércoles';
      case 4:
        return 'Jueves';
      case 5:
        return 'Viernes';
      case 6:
        return 'Sábado';
      case 7:
        return 'Domingo';
      default:
        return 'Día $weekday';
    }
  }
}
