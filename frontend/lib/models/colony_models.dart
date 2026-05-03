class Genotype {
  final int id;
  final String name;
  final String? description;
  final String? zygosity;

  Genotype({
    required this.id,
    required this.name,
    this.description,
    this.zygosity,
  });

  factory Genotype.fromJson(Map<String, dynamic> json) => Genotype(
        id: json['id'],
        name: json['name'],
        description: json['description'],
        zygosity: json['zygosity'],
      );
}

class Cage {
  final int id;
  final String label;
  final String? location;
  final int capacity;
  final int occupancy;

  Cage({
    required this.id,
    required this.label,
    this.location,
    required this.capacity,
    this.occupancy = 0,
  });

  factory Cage.fromJson(Map<String, dynamic> json) => Cage(
        id: json['id'],
        label: json['label'],
        location: json['location'],
        capacity: json['capacity'],
        occupancy: json['occupancy'] ?? 0,
      );
}

class Mouse {
  final int id;
  final String earTag;
  final String sex;
  final String dateOfBirth;
  final String status;
  final int? sireId;
  final int? damId;
  final int? genotypeId;
  final int? cageId;

  Mouse({
    required this.id,
    required this.earTag,
    required this.sex,
    required this.dateOfBirth,
    required this.status,
    this.sireId,
    this.damId,
    this.genotypeId,
    this.cageId,
  });

  factory Mouse.fromJson(Map<String, dynamic> json) => Mouse(
        id: json['id'],
        earTag: json['ear_tag'],
        sex: json['sex'],
        dateOfBirth: json['date_of_birth'],
        status: json['status'],
        sireId: json['sire_id'],
        damId: json['dam_id'],
        genotypeId: json['genotype_id'],
        cageId: json['cage_id'],
      );
}

class PedigreeNode {
  final int id;
  final String earTag;
  final String sex;
  final PedigreeNode? sire;
  final PedigreeNode? dam;

  PedigreeNode({
    required this.id,
    required this.earTag,
    required this.sex,
    this.sire,
    this.dam,
  });

  factory PedigreeNode.fromJson(Map<String, dynamic> json) => PedigreeNode(
        id: json['id'],
        earTag: json['ear_tag'],
        sex: json['sex'],
        sire: json['sire'] != null ? PedigreeNode.fromJson(json['sire']) : null,
        dam: json['dam'] != null ? PedigreeNode.fromJson(json['dam']) : null,
      );
}
