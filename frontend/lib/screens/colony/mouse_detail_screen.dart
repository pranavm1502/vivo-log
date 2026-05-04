import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/colony_providers.dart';
import '../../widgets/pedigree_widget.dart';

class MouseDetailScreen extends ConsumerStatefulWidget {
  final int mouseId;
  const MouseDetailScreen({super.key, required this.mouseId});

  @override
  ConsumerState<MouseDetailScreen> createState() => _MouseDetailScreenState();
}

class _MouseDetailScreenState extends ConsumerState<MouseDetailScreen> {
  bool _showPedigree = false;

  @override
  Widget build(BuildContext context) {
    final mouseAsync = ref.watch(mouseProvider(widget.mouseId));
    final genotypesAsync = ref.watch(genotypesProvider);
    final cagesAsync = ref.watch(cagesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Mouse Detail')),
      body: mouseAsync.when(
        data: (mouse) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Basic info
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Ear Tag: ${mouse.earTag}',
                          style: Theme.of(context).textTheme.headlineSmall),
                      const SizedBox(height: 8),
                      Text('Sex: ${mouse.sex}'),
                      Text('Date of Birth: ${mouse.dateOfBirth}'),
                      Text('Status: ${mouse.status}'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Status update
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Update Status',
                          style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      Row(
                        children: ['Alive', 'Deceased', 'Culled']
                            .map((s) => Padding(
                                  padding: const EdgeInsets.only(right: 8),
                                  child: ElevatedButton(
                                    onPressed: s == mouse.status
                                        ? null
                                        : () => _updateStatus(s),
                                    child: Text(s),
                                  ),
                                ))
                            .toList(),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Genotype assignment
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Genotype',
                          style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      genotypesAsync.when(
                        data: (genotypes) => DropdownButtonFormField<int?>(
                          value: mouse.genotypeId,
                          decoration:
                              const InputDecoration(border: OutlineInputBorder()),
                          items: [
                            const DropdownMenuItem(
                                value: null, child: Text('None')),
                            ...genotypes.map((g) => DropdownMenuItem(
                                  value: g.id,
                                  child: Text(g.name),
                                )),
                          ],
                          onChanged: (v) => _updateGenotype(v),
                        ),
                        loading: () => const CircularProgressIndicator(),
                        error: (e, _) => Text('Error: $e'),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Cage assignment
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Cage',
                          style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      cagesAsync.when(
                        data: (cages) => DropdownButtonFormField<int?>(
                          value: mouse.cageId,
                          decoration:
                              const InputDecoration(border: OutlineInputBorder()),
                          items: [
                            const DropdownMenuItem(
                                value: null, child: Text('None')),
                            ...cages.map((c) => DropdownMenuItem(
                                  value: c.id,
                                  child: Text(
                                      '${c.label} (${c.occupancy}/${c.capacity})'),
                                )),
                          ],
                          onChanged: (v) => _assignCage(v),
                        ),
                        loading: () => const CircularProgressIndicator(),
                        error: (e, _) => Text('Error: $e'),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Lineage
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Lineage',
                          style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      Text('Sire ID: ${mouse.sireId ?? "Not assigned"}'),
                      Text('Dam ID: ${mouse.damId ?? "Not assigned"}'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Pedigree
              ElevatedButton.icon(
                onPressed: () => setState(() => _showPedigree = !_showPedigree),
                icon: Icon(_showPedigree ? Icons.expand_less : Icons.expand_more),
                label: Text(_showPedigree ? 'Hide Pedigree' : 'Show Pedigree'),
              ),
              if (_showPedigree) ...[
                const SizedBox(height: 8),
                PedigreeWidget(mouseId: widget.mouseId),
              ],
            ],
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }

  Future<void> _updateStatus(String status) async {
    final repo = ref.read(colonyRepositoryProvider);
    await repo.updateMouse(widget.mouseId, {'status': status});
    ref.invalidate(mouseProvider(widget.mouseId));
  }

  Future<void> _updateGenotype(int? genotypeId) async {
    final repo = ref.read(colonyRepositoryProvider);
    await repo.updateMouse(widget.mouseId, {'genotype_id': genotypeId});
    ref.invalidate(mouseProvider(widget.mouseId));
  }

  Future<void> _assignCage(int? cageId) async {
    final repo = ref.read(colonyRepositoryProvider);
    await repo.assignCage(widget.mouseId, cageId);
    ref.invalidate(mouseProvider(widget.mouseId));
    ref.invalidate(cagesProvider);
  }
}
