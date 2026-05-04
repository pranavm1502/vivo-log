import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../api/study_repository.dart';
import '../../providers/study_providers.dart';
import '../../widgets/crud_dialogs.dart';

class MeasurementScreen extends ConsumerStatefulWidget {
  final int studyId;
  final int cohortId;
  final int enrollmentId;

  const MeasurementScreen({
    super.key,
    required this.studyId,
    required this.cohortId,
    required this.enrollmentId,
  });

  @override
  ConsumerState<MeasurementScreen> createState() => _MeasurementScreenState();
}

class _MeasurementScreenState extends ConsumerState<MeasurementScreen> {
  final _lengthCtrl = TextEditingController();
  final _widthCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();

  double? get _previewVolume {
    final l = double.tryParse(_lengthCtrl.text);
    final w = double.tryParse(_widthCtrl.text);
    if (l != null && w != null && l >= 0 && w >= 0) {
      return l * w * w / 2.0;
    }
    return null;
  }

  @override
  void dispose() {
    _lengthCtrl.dispose();
    _widthCtrl.dispose();
    _weightCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final measurementsAsync = ref.watch(measurementsProvider((
      studyId: widget.studyId,
      cohortId: widget.cohortId,
      enrollmentId: widget.enrollmentId,
    )));

    return Scaffold(
      appBar: AppBar(title: const Text('Measurements')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Entry form
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('New Measurement',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _lengthCtrl,
                          decoration: const InputDecoration(
                            labelText: 'Tumor Length (mm)',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextField(
                          controller: _widthCtrl,
                          decoration: const InputDecoration(
                            labelText: 'Tumor Width (mm)',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  // Live volume preview
                  if (_previewVolume != null)
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.teal.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'Volume preview: ${_previewVolume!.toStringAsFixed(2)} mm³',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _weightCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Body Weight (g)',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _notesCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Notes',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: _saveMeasurement,
                    icon: const Icon(Icons.save),
                    label: const Text('Save Measurement'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // History table
          Text('Measurement History',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          measurementsAsync.when(
            data: (measurements) => measurements.isEmpty
                ? const Text('No measurements recorded')
                : SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      columns: const [
                        DataColumn(label: Text('Date')),
                        DataColumn(label: Text('Length')),
                        DataColumn(label: Text('Width')),
                        DataColumn(label: Text('Volume')),
                        DataColumn(label: Text('Weight')),
                        DataColumn(label: Text('Notes')),
                        DataColumn(label: Text('')),
                      ],
                      rows: measurements
                          .map((m) => DataRow(cells: [
                                DataCell(Text(m.recordedAt.substring(0, 16))),
                                DataCell(Text(m.tumorLengthMm?.toStringAsFixed(1) ?? '-')),
                                DataCell(Text(m.tumorWidthMm?.toStringAsFixed(1) ?? '-')),
                                DataCell(Text(
                                    m.tumorVolumeMm3?.toStringAsFixed(2) ?? '-')),
                                DataCell(Text(
                                    m.bodyWeightG?.toStringAsFixed(1) ?? '-')),
                                DataCell(Text(m.notes ?? '')),
                                DataCell(IconButton(
                                  icon: const Icon(Icons.delete, size: 18),
                                  onPressed: () async {
                                    final deleted = await showDeleteConfirmation(
                                      context,
                                      entityName: 'measurement from ${m.recordedAt.substring(0, 10)}',
                                      onDelete: () => StudyRepository().deleteMeasurement(
                                        widget.studyId,
                                        widget.cohortId,
                                        widget.enrollmentId,
                                        m.id,
                                      ),
                                    );
                                    if (deleted) {
                                      ref.invalidate(measurementsProvider((
                                        studyId: widget.studyId,
                                        cohortId: widget.cohortId,
                                        enrollmentId: widget.enrollmentId,
                                      )));
                                    }
                                  },
                                )),
                              ]))
                          .toList(),
                    ),
                  ),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => Text('Error: $e'),
          ),
        ],
      ),
    );
  }

  Future<void> _saveMeasurement() async {
    final data = <String, dynamic>{};
    final l = double.tryParse(_lengthCtrl.text);
    final w = double.tryParse(_widthCtrl.text);
    final bw = double.tryParse(_weightCtrl.text);
    if (l != null) data['tumor_length_mm'] = l;
    if (w != null) data['tumor_width_mm'] = w;
    if (bw != null) data['body_weight_g'] = bw;
    if (_notesCtrl.text.isNotEmpty) data['notes'] = _notesCtrl.text;

    try {
      await ref.read(studyRepositoryProvider).createMeasurement(
            widget.studyId,
            widget.cohortId,
            widget.enrollmentId,
            data,
          );
      ref.invalidate(measurementsProvider((
        studyId: widget.studyId,
        cohortId: widget.cohortId,
        enrollmentId: widget.enrollmentId,
      )));
      _lengthCtrl.clear();
      _widthCtrl.clear();
      _weightCtrl.clear();
      _notesCtrl.clear();
      setState(() {});
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Measurement saved')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }
}
