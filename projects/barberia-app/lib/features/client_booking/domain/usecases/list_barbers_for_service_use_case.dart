import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/barber_summary.dart';
import '../repositories/booking_repository.dart';

class ListBarbersForServiceParams {
  const ListBarbersForServiceParams(this.serviceId);

  final String serviceId;
}

class ListBarbersForServiceUseCase
    extends UseCase<List<BarberSummary>, ListBarbersForServiceParams> {
  ListBarbersForServiceUseCase(this._repository);

  final BookingRepository _repository;

  @override
  Future<Result<List<BarberSummary>>> call(ListBarbersForServiceParams params) {
    return _repository.listBarbersForService(params.serviceId);
  }
}
