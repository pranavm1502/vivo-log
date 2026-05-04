import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../api/colony_repository.dart';
import '../../api/error_utils.dart';
import '../../models/colony_models.dart';
import '../../providers/colony_providers.dart';
import '../../widgets/crud_dialogs.dart';

class MouseFormScreen extends ConsumerStatefulWidget {
  final Mouse? existing;

  const MouseFormScreen({super.key, this.existing});

  @override
  ConsumerState<MouseFormScreen> createState() => _MouseFormScreenState();
}

class _MouseFormScreenState extends ConsumerState<MouseFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _earTagController;
  String _sex = 'Male';
  DateTime _dob = DateTime.now();
  int? _genotypeId;
  int? _cageId;
  String _status = 'Alive';
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final m = widget.existing;
    _earTagController = TextEditingController(text: m?.earTag ?? '');
    if (m != null) {
      _sex = m.sex;
      _dob = DateTime.tryParse(m.dateOfBirth) ?? DateTime.now();
      _genotypeId = m.genotypeId;
      _cageId = m.cageId;
      _status = m.status;
    }
  }

  @override
  void dispose() {
    _earTagController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);

    final data = {
      'ear_tag': _earTagController.text.trim(),
      'sex': _sex,
      'date_of_birth': '${_dob.year}-${_dob.month.toString().padLeft(2, '0')}-${_dob.day.toString().padLeft(2, '0')}',
      'genotype_id': _genotypeId,
      'cage_id': _cageId,
      if (widget.existing != null) 'status': _status,
    };

    try {
      final repo = ColonyRepository();
      if (widget.existing == null) {
        await repo.createMouse(data);
      } else {
        await repo.updateMouse(widget.existing!.id, data);
      }
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(extractErrorMessage(e))),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final genotypesAsync = ref.watch(genotypesProvider);
    final cagesAsync = ref.watch(cagesProvider);
    final isEdit = widget.existing != null;

    return Scaffold(
      appBar: AppBar(title: Text(isEdit ? 'Edit Mouse' : 'New Mouse')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _earTagController,
                decoration: const InputDecoration(labelText: 'Ear Tag *', border: OutlineInputBorder()),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Ear tag is required' : null,
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _sex,
                decoration: const InputDecoration(labelText: 'Sex *', border: OutlineInputBorder()),
                items: const [
                  DropdownMenuItem(value: 'Male', child: Text('Male')),
                  DropdownMenuItem(value: 'Female', child: Text('Female')),
                ],
                onChanged: (v) => setState(() => _sex = v!),
              ),
              const SizedBox(height: 16),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Date of Birth'),
                subtitle: Text('${_dob.year}-${_dob.month.toString().padLeft(2, '0')}-${_dob.day.toString().padLeft(2, '0')}'),
                trailing: const Icon(Icons.calendar_today),
                onTap: () async {
                  final picked = await showDatePicker(
                    context: context,
                    initialDate: _dob,
                    firstDate: DateTime(2020),
                    lastDate: DateTime.now(),
                  );
                  if (picked != null) setState(() => _dob = picked);
                },
              ),
              const SizedBox(height: 16),
              genotypesAsync.when(
                data: (genotypes) => Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<int?>(
                        value: _genotypeId,
                        decoration: const InputDecoration(labelText: 'Genotype', border: OutlineInputBorder()),
                        items: [
                          const DropdownMenuItem(value: null, child: Text('None')),
                          ...genotypes.map((g) => DropdownMenuItem(value: g.id, child: Text(g.name))),
                        ],
                        onChanged: (v) => setState(() => _genotypeId = v),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline),
                      tooltip: 'Add New Genotype',
                      onPressed: () async {
                        final created = await showGenotypeDialog(context);
                        if (created) {
                          ref.invalidate(genotypesProvider);
                        }
                      },
                    ),
                  ],
                ),
                loading: () => const LinearProgressIndicator(),
                error: (_, __) => const Text('Error loading genotypes'),
              ),
              const SizedBox(height: 16),
              cagesAsync.when(
                data: (cages) => Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<int?>(
                        value: _cageId,
                        decoration: const InputDecoration(labelText: 'Cage', border: OutlineInputBorder()),
                        items: [
                          const DropdownMenuItem(value: null, child: Text('None')),
                          ...cages.map((c) => DropdownMenuItem(value: c.id, child: Text('${c.label} (${c.occupancy}/${c.capacity})'))),
                        ],
                        onChanged: (v) => setState(() => _cageId = v),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline),
                      tooltip: 'Add New Cage',
                      onPressed: () async {
                        final created = await showCageDialog(context);
                        if (created) {
                          ref.invalidate(cagesProvider);
                        }
                      },
                    ),
                  ],
                ),
                loading: () => const LinearProgressIndicator(),
                error: (_, __) => const Text('Error loading cages'),
              ),
              if (isEdit) ...[
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _status,
                  decoration: const InputDecoration(labelText: 'Status', border: OutlineInputBorder()),
                  items: const [
                    DropdownMenuItem(value: 'Alive', child: Text('Alive')),
                    DropdownMenuItem(value: 'Deceased', child: Text('Deceased')),
                    DropdownMenuItem(value: 'Culled', child: Text('Culled')),
                  ],
                  onChanged: (v) => setState(() => _status = v!),
                ),
              ],
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _saving ? null : _save,
                child: _saving
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                    : Text(isEdit ? 'Save' : 'Create'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
