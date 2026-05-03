import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/colony_providers.dart';
import '../../providers/study_providers.dart';
import 'measurement_screen.dart';

class CohortEnrollmentScreen extends ConsumerWidget {
  final int studyId;
  final int cohortId;
  final String cohortName;

  const CohortEnrollmentScreen({
    super.key,
    required this.studyId,
    required this.cohortId,
    required this.cohortName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final enrollmentsAsync = ref.watch(
      enrollmentsProvider((studyId: studyId, cohortId: cohortId)),
    );
    final miceAsync = ref.watch(allMiceProvider);

    return Scaffold(
      appBar: AppBar(title: Text('Cohort: $cohortName')),
      body: enrollmentsAsync.when(
        data: (enrollments) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text('Enrollments (${enrollments.length})',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            if (enrollments.isEmpty)
              const Text('No mice enrolled yet')
            else
              ...enrollments.map((e) => Card(
                    child: ListTile(
                      title: Text('Mouse #${e.mouseId}'),
                      subtitle: Text(e.removedAt != null
                          ? 'Removed: ${e.removalReason ?? "N/A"}'
                          : 'Enrolled: ${e.enrolledAt}'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => MeasurementScreen(
                            studyId: studyId,
                            cohortId: cohortId,
                            enrollmentId: e.id,
                          ),
                        ),
                      ),
                    ),
                  )),
            const Divider(height: 32),
            Text('Enroll Mouse', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            miceAsync.when(
              data: (mice) {
                // Filter: only show Alive mice
                final eligible =
                    mice.where((m) => m.status == 'Alive').toList();
                return eligible.isEmpty
                    ? const Text('No eligible mice')
                    : Column(
                        children: eligible
                            .map((m) => ListTile(
                                  title: Text(m.earTag),
                                  subtitle: Text('${m.sex} · ${m.status}'),
                                  trailing: ElevatedButton(
                                    onPressed: () =>
                                        _enrollMouse(context, ref, m.id),
                                    child: const Text('Enroll'),
                                  ),
                                ))
                            .toList(),
                      );
              },
              loading: () => const CircularProgressIndicator(),
              error: (e, _) => Text('Error: $e'),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }

  Future<void> _enrollMouse(
      BuildContext context, WidgetRef ref, int mouseId) async {
    try {
      await ref
          .read(studyRepositoryProvider)
          .enrollMouse(studyId, cohortId, mouseId);
      ref.invalidate(
          enrollmentsProvider((studyId: studyId, cohortId: cohortId)));
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Mouse enrolled')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }
}
