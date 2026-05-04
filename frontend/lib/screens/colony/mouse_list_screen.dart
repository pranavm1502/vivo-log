import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../api/colony_repository.dart';
import '../../api/export_repository.dart';
import '../../providers/colony_providers.dart';
import '../../widgets/crud_dialogs.dart';
import '../../widgets/export_helper.dart';
import 'mouse_detail_screen.dart';
import 'mouse_form_screen.dart';

class MouseListScreen extends ConsumerStatefulWidget {
  const MouseListScreen({super.key});

  @override
  ConsumerState<MouseListScreen> createState() => _MouseListScreenState();
}

class _MouseListScreenState extends ConsumerState<MouseListScreen> {
  int? _selectedGenotypeId;
  String? _selectedStatus;

  @override
  Widget build(BuildContext context) {
    final miceAsync = ref.watch(
      miceProvider((genotypeId: _selectedGenotypeId, status: _selectedStatus)),
    );
    final genotypesAsync = ref.watch(genotypesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mice'),
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            tooltip: 'Export',
            onPressed: () => showExportDialog(
              context,
              title: 'mice',
              fetchData: (fmt) => ExportRepository().exportMice(format: fmt),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter bar
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                // Genotype filter
                Expanded(
                  child: genotypesAsync.when(
                    data: (genotypes) => DropdownButtonFormField<int?>(
                      value: _selectedGenotypeId,
                      decoration: const InputDecoration(
                        labelText: 'Genotype',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                      items: [
                        const DropdownMenuItem(value: null, child: Text('All')),
                        ...genotypes.map((g) => DropdownMenuItem(
                              value: g.id,
                              child: Text(g.name),
                            )),
                      ],
                      onChanged: (v) => setState(() => _selectedGenotypeId = v),
                    ),
                    loading: () => const SizedBox.shrink(),
                    error: (_, __) => const SizedBox.shrink(),
                  ),
                ),
                const SizedBox(width: 8),
                // Status filter
                Expanded(
                  child: DropdownButtonFormField<String?>(
                    value: _selectedStatus,
                    decoration: const InputDecoration(
                      labelText: 'Status',
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                    items: const [
                      DropdownMenuItem(value: null, child: Text('All')),
                      DropdownMenuItem(value: 'Alive', child: Text('Alive')),
                      DropdownMenuItem(value: 'Deceased', child: Text('Deceased')),
                      DropdownMenuItem(value: 'Culled', child: Text('Culled')),
                    ],
                    onChanged: (v) => setState(() => _selectedStatus = v),
                  ),
                ),
              ],
            ),
          ),
          // Mouse list
          Expanded(
            child: miceAsync.when(
              data: (mice) => mice.isEmpty
                  ? const Center(child: Text('No mice found'))
                  : ListView.builder(
                      itemCount: mice.length,
                      itemBuilder: (context, index) {
                        final m = mice[index];
                        return ListTile(
                          title: Text(m.earTag),
                          subtitle: Text('${m.sex} · ${m.status}'),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(m.dateOfBirth),
                              IconButton(
                                icon: const Icon(Icons.delete, size: 20),
                                onPressed: () async {
                                  final deleted = await showDeleteConfirmation(
                                    context,
                                    entityName: m.earTag,
                                    onDelete: () => ColonyRepository().deleteMouse(m.id),
                                  );
                                  if (deleted) {
                                    ref.invalidate(miceProvider);
                                    ref.invalidate(allMiceProvider);
                                  }
                                },
                              ),
                            ],
                          ),
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => MouseDetailScreen(mouseId: m.id),
                            ),
                          ),
                        );
                      },
                    ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Error: $e')),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push<bool>(
            context,
            MaterialPageRoute(builder: (_) => const MouseFormScreen()),
          );
          if (result == true) {
            ref.invalidate(miceProvider);
            ref.invalidate(allMiceProvider);
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
