import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/colony_models.dart';
import '../providers/colony_providers.dart';

class PedigreeWidget extends ConsumerWidget {
  final int mouseId;
  const PedigreeWidget({super.key, required this.mouseId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pedigreeAsync = ref.watch(pedigreeProvider(mouseId));

    return pedigreeAsync.when(
      data: (node) => SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: _buildNode(context, node, 0),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Text('Error loading pedigree: $e'),
    );
  }

  Widget _buildNode(BuildContext context, PedigreeNode node, int depth) {
    final color = node.sex == 'Male' ? Colors.blue.shade50 : Colors.pink.shade50;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          margin: const EdgeInsets.all(4),
          decoration: BoxDecoration(
            color: color,
            border: Border.all(color: Colors.grey),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            children: [
              Text(node.earTag, style: const TextStyle(fontWeight: FontWeight.bold)),
              Text(node.sex, style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
        if (node.sire != null || node.dam != null)
          Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (node.sire != null) _buildNode(context, node.sire!, depth + 1),
              if (node.dam != null) _buildNode(context, node.dam!, depth + 1),
            ],
          ),
      ],
    );
  }
}
