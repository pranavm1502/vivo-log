import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/study_providers.dart';
import 'study_detail_screen.dart';

class StudyListScreen extends ConsumerWidget {
  const StudyListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final studiesAsync = ref.watch(studiesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Studies')),
      body: studiesAsync.when(
        data: (studies) => studies.isEmpty
            ? const Center(child: Text('No studies'))
            : ListView.builder(
                itemCount: studies.length,
                itemBuilder: (context, index) {
                  final s = studies[index];
                  return ListTile(
                    title: Text(s.name),
                    subtitle: Text('${s.status} · Started ${s.startDate}'),
                    trailing: _statusChip(s.status),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => StudyDetailScreen(studyId: s.id),
                      ),
                    ),
                  );
                },
              ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }

  Widget _statusChip(String status) {
    final color = switch (status) {
      'Active' => Colors.green,
      'Completed' => Colors.grey,
      _ => Colors.orange,
    };
    return Chip(
      label: Text(status, style: const TextStyle(fontSize: 12)),
      backgroundColor: color.withValues(alpha: 0.2),
      side: BorderSide.none,
    );
  }
}
