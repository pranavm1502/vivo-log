import 'package:flutter/material.dart';
import '../../api/study_repository.dart';
import '../../api/error_utils.dart';
import '../../models/study_models.dart';

/// Shows a dialog for creating or editing a cohort.
Future<bool> showCohortDialog(
  BuildContext context, {
  required int studyId,
  Cohort? existing,
}) async {
  final nameController = TextEditingController(text: existing?.name ?? '');
  final descController = TextEditingController(text: existing?.description ?? '');
  final formKey = GlobalKey<FormState>();
  final repo = StudyRepository();

  final result = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(existing == null ? 'New Cohort' : 'Edit Cohort'),
      content: Form(
        key: formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Cohort Name *'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Name is required' : null,
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: descController,
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 2,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
        FilledButton(
          onPressed: () async {
            if (!formKey.currentState!.validate()) return;
            final data = {
              'name': nameController.text.trim(),
              if (descController.text.trim().isNotEmpty)
                'description': descController.text.trim(),
            };
            try {
              if (existing == null) {
                await repo.createCohort(studyId, data);
              } else {
                await repo.updateCohort(studyId, existing.id, data);
              }
              if (ctx.mounted) Navigator.pop(ctx, true);
            } catch (e) {
              if (ctx.mounted) {
                ScaffoldMessenger.of(ctx).showSnackBar(
                  SnackBar(content: Text(extractErrorMessage(e))),
                );
              }
            }
          },
          child: Text(existing == null ? 'Create' : 'Save'),
        ),
      ],
    ),
  );
  return result ?? false;
}
