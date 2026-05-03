import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/study_providers.dart';
import 'cohort_enrollment_screen.dart';

class StudyDetailScreen extends ConsumerWidget {
  final int studyId;
  const StudyDetailScreen({super.key, required this.studyId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final studyAsync = ref.watch(studyProvider(studyId));
    final cohortsAsync = ref.watch(cohortsProvider(studyId));

    return Scaffold(
      appBar: AppBar(title: const Text('Study Detail')),
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
            Text('Cohorts', style: Theme.of(context).textTheme.titleMedium),
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
                                  trailing: const Icon(Icons.chevron_right),
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
