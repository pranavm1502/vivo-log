import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../api/study_repository.dart';
import '../../providers/study_providers.dart';
import '../../widgets/crud_dialogs.dart';
import 'study_detail_screen.dart';
import 'study_form_screen.dart';

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
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _statusChip(s.status),
                        IconButton(
                          icon: const Icon(Icons.delete, size: 20),
                          onPressed: () async {
                            final deleted = await showDeleteConfirmation(
                              context,
                              entityName: s.name,
                              onDelete: () => StudyRepository().deleteStudy(s.id),
                            );
                            if (deleted) ref.invalidate(studiesProvider);
                          },
                        ),
                      ],
                    ),
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
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push<bool>(
            context,
            MaterialPageRoute(builder: (_) => const StudyFormScreen()),
          );
          if (result == true) ref.invalidate(studiesProvider);
        },
        child: const Icon(Icons.add),
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
