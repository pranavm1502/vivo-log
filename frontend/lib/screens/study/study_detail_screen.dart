import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../api/export_repository.dart';
import '../../api/study_repository.dart';
import '../../providers/study_providers.dart';
import '../../widgets/cohort_dialog.dart';
import '../../widgets/crud_dialogs.dart';
import '../../widgets/export_helper.dart';
import 'cohort_enrollment_screen.dart';
import 'study_form_screen.dart';

class StudyDetailScreen extends ConsumerWidget {
  final int studyId;
  const StudyDetailScreen({super.key, required this.studyId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final studyAsync = ref.watch(studyProvider(studyId));
    final cohortsAsync = ref.watch(cohortsProvider(studyId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Study Detail'),
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            tooltip: 'Export Data',
            onPressed: () => showExportDialog(
              context,
              title: 'study_$studyId',
              fetchData: (fmt) => ExportRepository().exportStudyMeasurements(studyId, format: fmt),
            ),
          ),
          studyAsync.when(
            data: (study) => IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () async {
                final result = await Navigator.push<bool>(
                  context,
                  MaterialPageRoute(builder: (_) => StudyFormScreen(existing: study)),
                );
                if (result == true) ref.invalidate(studyProvider(studyId));
              },
            ),
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
        ],
      ),
      body: studyAsync.when(
        data: (study) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(study.name,
                        style: Theme.of(context).textTheme.headlineSmall),
                    const SizedBox(height: 8),
                    Text('Status: ${study.status}'),
                    Text('Start: ${study.startDate}'),
                    if (study.endDate != null) Text('End: ${study.endDate}'),
                    if (study.description != null) ...[
                      const SizedBox(height: 8),
                      Text(study.description!),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Cohorts', style: Theme.of(context).textTheme.titleMedium),
                IconButton(
                  icon: const Icon(Icons.add),
                  tooltip: 'Add Cohort',
                  onPressed: () async {
                    final created = await showCohortDialog(context, studyId: studyId);
                    if (created) ref.invalidate(cohortsProvider(studyId));
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            cohortsAsync.when(
              data: (cohorts) => cohorts.isEmpty
                  ? const Text('No cohorts defined')
                  : Column(
                      children: cohorts
                          .map((c) => Card(
                                child: ListTile(
                                  title: Text(c.name),
                                  subtitle:
                                      Text(c.description ?? 'No description'),
                                  trailing: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      IconButton(
                                        icon: const Icon(Icons.edit, size: 20),
                                        onPressed: () async {
                                          final changed = await showCohortDialog(
                                            context,
                                            studyId: studyId,
                                            existing: c,
                                          );
                                          if (changed) ref.invalidate(cohortsProvider(studyId));
                                        },
                                      ),
                                      IconButton(
                                        icon: const Icon(Icons.delete, size: 20),
                                        onPressed: () async {
                                          final deleted = await showDeleteConfirmation(
                                            context,
                                            entityName: c.name,
                                            onDelete: () => StudyRepository().deleteCohort(studyId, c.id),
                                          );
                                          if (deleted) ref.invalidate(cohortsProvider(studyId));
                                        },
                                      ),
                                      const Icon(Icons.chevron_right),
                                    ],
                                  ),
                                  onTap: () => Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (_) => CohortEnrollmentScreen(
                                        studyId: studyId,
                                        cohortId: c.id,
                                        cohortName: c.name,
                                      ),
                                    ),
                                  ),
                                ),
                              ))
                          .toList(),
                    ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Error: $e'),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
