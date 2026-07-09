class BusinessHoursDay {
  const BusinessHoursDay({
    required this.weekday,
    required this.openTime,
    required this.closeTime,
    required this.isClosed,
  });

  final int weekday;
  final String openTime;
  final String closeTime;
  final bool isClosed;

  BusinessHoursDay copyWith({
    int? weekday,
    String? openTime,
    String? closeTime,
    bool? isClosed,
  }) {
    return BusinessHoursDay(
      weekday: weekday ?? this.weekday,
      openTime: openTime ?? this.openTime,
      closeTime: closeTime ?? this.closeTime,
      isClosed: isClosed ?? this.isClosed,
    );
  }

  static List<BusinessHoursDay> defaultWeek() {
    return List.generate(
      7,
      (index) => BusinessHoursDay(
        weekday: index + 1,
        openTime: '09:00:00',
        closeTime: '18:00:00',
        isClosed: false,
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
