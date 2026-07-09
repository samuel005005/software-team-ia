import '../../../../../core/utils/result.dart';
import '../entities/admin_client.dart';
import '../entities/admin_client_appointment.dart';

abstract class AdminClientsRepository {
  Future<Result<List<AdminClient>>> listClients();

  Future<Result<AdminClient>> updateClient({
    required String userId,
    bool? isActive,
  });

  Future<Result<List<AdminClientAppointment>>> listClientAppointments(String userId);

  Future<Result<AdminClientAppointment>> voidAppointment({
    required String appointmentId,
    required String reason,
  });
}
