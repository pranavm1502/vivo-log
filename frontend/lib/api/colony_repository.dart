import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../models/colony_models.dart';

class ColonyRepository {
  final Dio _dio = ApiClient().dio;

  // ── Genotypes ──
  Future<List<Genotype>> getGenotypes() async {
    final r = await _dio.get('/colony/genotypes');
    return (r.data as List).map((e) => Genotype.fromJson(e)).toList();
  }

  Future<Genotype> createGenotype(Map<String, dynamic> data) async {
    final r = await _dio.post('/colony/genotypes', data: data);
    return Genotype.fromJson(r.data);
  }

  // ── Cages ──
  Future<List<Cage>> getCages() async {
    final r = await _dio.get('/colony/cages');
    return (r.data as List).map((e) => Cage.fromJson(e)).toList();
  }

  Future<Cage> getCage(int id) async {
    final r = await _dio.get('/colony/cages/$id');
    return Cage.fromJson(r.data);
  }

  Future<Cage> createCage(Map<String, dynamic> data) async {
    final r = await _dio.post('/colony/cages', data: data);
    return Cage.fromJson(r.data);
  }

  // ── Mice ──
  Future<List<Mouse>> getMice({int? genotypeId, String? status}) async {
    final params = <String, dynamic>{};
    if (genotypeId != null) params['genotype_id'] = genotypeId;
    if (status != null) params['status'] = status;
    final r = await _dio.get('/colony/mice', queryParameters: params);
    return (r.data as List).map((e) => Mouse.fromJson(e)).toList();
  }

  Future<Mouse> getMouse(int id) async {
    final r = await _dio.get('/colony/mice/$id');
    return Mouse.fromJson(r.data);
  }

  Future<Mouse> createMouse(Map<String, dynamic> data) async {
    final r = await _dio.post('/colony/mice', data: data);
    return Mouse.fromJson(r.data);
  }

  Future<Mouse> updateMouse(int id, Map<String, dynamic> data) async {
    final r = await _dio.patch('/colony/mice/$id', data: data);
    return Mouse.fromJson(r.data);
  }

  Future<Mouse> assignLineage(int id, Map<String, dynamic> data) async {
    final r = await _dio.put('/colony/mice/$id/lineage', data: data);
    return Mouse.fromJson(r.data);
  }

  Future<Mouse> assignCage(int id, int? cageId) async {
    final r = await _dio.put('/colony/mice/$id/cage', data: {'cage_id': cageId});
    return Mouse.fromJson(r.data);
  }

  Future<PedigreeNode> getPedigree(int id, {int depth = 3}) async {
    final r = await _dio.get('/colony/mice/$id/pedigree', queryParameters: {'depth': depth});
    return PedigreeNode.fromJson(r.data);
  }
}
