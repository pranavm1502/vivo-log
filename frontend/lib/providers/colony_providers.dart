import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/colony_repository.dart';
import '../models/colony_models.dart';

final colonyRepositoryProvider = Provider((ref) => ColonyRepository());

final miceProvider = FutureProvider.family<List<Mouse>, ({int? genotypeId, String? status})>(
  (ref, params) =>
      ref.read(colonyRepositoryProvider).getMice(genotypeId: params.genotypeId, status: params.status),
);

final allMiceProvider = FutureProvider<List<Mouse>>(
  (ref) => ref.read(colonyRepositoryProvider).getMice(),
);

final mouseProvider = FutureProvider.family<Mouse, int>(
  (ref, id) => ref.read(colonyRepositoryProvider).getMouse(id),
);

final genotypesProvider = FutureProvider<List<Genotype>>(
  (ref) => ref.read(colonyRepositoryProvider).getGenotypes(),
);

final cagesProvider = FutureProvider<List<Cage>>(
  (ref) => ref.read(colonyRepositoryProvider).getCages(),
);

final pedigreeProvider = FutureProvider.family<PedigreeNode, int>(
  (ref, mouseId) => ref.read(colonyRepositoryProvider).getPedigree(mouseId),
);
