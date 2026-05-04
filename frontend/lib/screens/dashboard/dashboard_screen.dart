import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/analytics_models.dart';
import '../../providers/analytics_providers.dart';
import '../study/study_detail_screen.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardAsync = ref.watch(dashboardProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: dashboardAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (studies) {
          if (studies.isEmpty) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.analytics_outlined, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('No active studies', style: TextStyle(fontSize: 18, color: Colors.grey)),
                  SizedBox(height: 8),
                  Text('Create a study and mark it as Active to see analytics here.', style: TextStyle(color: Colors.grey)),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(dashboardProvider),
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: studies.length,
              itemBuilder: (ctx, i) => _StudyCard(study: studies[i]),
            ),
          );
        },
      ),
    );
  }
}

class _StudyCard extends StatelessWidget {
  final DashboardStudy study;

  const _StudyCard({required this.study});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => StudyDetailScreen(studyId: study.studyId)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(study.studyName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Row(
                children: [
                  _metric('Days', study.daysElapsed.toString()),
                  _metric('Cohorts', study.cohortCount.toString()),
                  _metric('Enrolled', study.totalEnrollments.toString()),
                  _metric('Measurements', study.totalMeasurements.toString()),
                ],
              ),
              if (study.latestMeanVolume != null) ...[
                const SizedBox(height: 8),
                Text(
                  'Latest mean volume: ${study.latestMeanVolume!.toStringAsFixed(1)} mm³',
                  style: TextStyle(color: Colors.grey[700], fontSize: 13),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _metric(String label, String value) {
    return Expanded(
      child: Column(
        children: [
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        ],
      ),
    );
  }
}
