import 'package:flutter/material.dart';

import '../../api/error_utils.dart';
import '../../api/colony_repository.dart';
import '../../models/colony_models.dart';

/// Shows a dialog for creating or editing a genotype.
Future<bool> showGenotypeDialog(
  BuildContext context, {
  Genotype? existing,
}) async {
  final nameController = TextEditingController(text: existing?.name ?? '');
  final descController = TextEditingController(text: existing?.description ?? '');
  final zygosityController = TextEditingController(text: existing?.zygosity ?? '');
  final formKey = GlobalKey<FormState>();
  final repo = ColonyRepository();

  final result = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(existing == null ? 'New Genotype' : 'Edit Genotype'),
      content: Form(
        key: formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Name *'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Name is required' : null,
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: descController,
              decoration: const InputDecoration(labelText: 'Description'),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: zygosityController,
              decoration: const InputDecoration(labelText: 'Zygosity'),
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
              'description': descController.text.trim().isEmpty ? null : descController.text.trim(),
              'zygosity': zygosityController.text.trim().isEmpty ? null : zygosityController.text.trim(),
            };
            try {
              if (existing == null) {
                await repo.createGenotype(data);
              } else {
                await repo.updateGenotype(existing.id, data);
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

/// Shows a dialog for creating or editing a cage.
Future<bool> showCageDialog(
  BuildContext context, {
  Cage? existing,
}) async {
  final labelController = TextEditingController(text: existing?.label ?? '');
  final locationController = TextEditingController(text: existing?.location ?? '');
  final capacityController = TextEditingController(text: existing?.capacity.toString() ?? '5');
  final formKey = GlobalKey<FormState>();
  final repo = ColonyRepository();

  final result = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(existing == null ? 'New Cage' : 'Edit Cage'),
      content: Form(
        key: formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: labelController,
              decoration: const InputDecoration(labelText: 'Label *'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Label is required' : null,
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: locationController,
              decoration: const InputDecoration(labelText: 'Location'),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: capacityController,
              decoration: const InputDecoration(labelText: 'Capacity *'),
              keyboardType: TextInputType.number,
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'Capacity is required';
                final n = int.tryParse(v.trim());
                if (n == null || n < 1) return 'Capacity must be at least 1';
                return null;
              },
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
              'label': labelController.text.trim(),
              'location': locationController.text.trim().isEmpty ? null : locationController.text.trim(),
              'capacity': int.parse(capacityController.text.trim()),
            };
            try {
              if (existing == null) {
                await repo.createCage(data);
              } else {
                await repo.updateCage(existing.id, data);
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

/// Shows a confirmation dialog before delete, handles 409.
Future<bool> showDeleteConfirmation(
  BuildContext context, {
  required String entityName,
  required Future<void> Function() onDelete,
}) async {
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Confirm Delete'),
      content: Text('Are you sure you want to delete "$entityName"?'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
        FilledButton(
          style: FilledButton.styleFrom(backgroundColor: Colors.red),
          onPressed: () => Navigator.pop(ctx, true),
          child: const Text('Delete'),
        ),
      ],
    ),
  );
  if (confirmed != true) return false;

  try {
    await onDelete();
    return true;
  } catch (e) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(extractErrorMessage(e))),
      );
    }
    return false;
  }
}
