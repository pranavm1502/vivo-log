import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/colony_providers.dart';

class CageListScreen extends ConsumerWidget {
  const CageListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cagesAsync = ref.watch(cagesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Cages')),
      body: cagesAsync.when(
        data: (cages) => cages.isEmpty
            ? const Center(child: Text('No cages'))
            : ListView.builder(
                itemCount: cages.length,
                itemBuilder: (context, index) {
                  final c = cages[index];
                  return ListTile(
                    title: Text(c.label),
                    subtitle: Text(c.location ?? 'No location'),
                    trailing: Text('${c.occupancy}/${c.capacity}'),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => CageDetailScreen(cageId: c.id),
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
}

class CageDetailScreen extends ConsumerWidget {
  final int cageId;
  const CageDetailScreen({super.key, required this.cageId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final allMiceAsync = ref.watch(allMiceProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Cage Detail')),
      body: allMiceAsync.when(
        data: (mice) {
          final cageMice = mice.where((m) => m.cageId == cageId).toList();
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text('Mice in cage: ${cageMice.length}',
                  style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              if (cageMice.isEmpty)
                const Text('No mice assigned')
              else
                ...cageMice.map((m) => ListTile(
                      title: Text(m.earTag),
                      subtitle: Text('${m.sex} · ${m.status}'),
                    )),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
