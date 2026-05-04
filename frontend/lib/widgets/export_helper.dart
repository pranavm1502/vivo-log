import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

/// Shows format picker and triggers export, saving directly to Downloads.
Future<void> showExportDialog(
  BuildContext context, {
  required String title,
  required Future<Uint8List> Function(String format) fetchData,
}) async {
  final format = await showDialog<String>(
    context: context,
    builder: (ctx) => SimpleDialog(
      title: Text('Export $title'),
      children: [
        SimpleDialogOption(
          onPressed: () => Navigator.pop(ctx, 'csv'),
          child: const Text('CSV (.csv)'),
        ),
        SimpleDialogOption(
          onPressed: () => Navigator.pop(ctx, 'xlsx'),
          child: const Text('Excel (.xlsx)'),
        ),
      ],
    ),
  );
  if (format == null || !context.mounted) return;

  try {
    final bytes = await fetchData(format);
    final dir = await getDownloadsDirectory();
    if (dir == null) throw Exception('Could not access Downloads folder');
    final ext = format == 'xlsx' ? 'xlsx' : 'csv';
    final now = DateTime.now();
    final timestamp = '${now.year}${now.month.toString().padLeft(2, '0')}${now.day.toString().padLeft(2, '0')}_${now.hour.toString().padLeft(2, '0')}${now.minute.toString().padLeft(2, '0')}${now.second.toString().padLeft(2, '0')}';
    final fileName = '${title.replaceAll(' ', '_')}_$timestamp.$ext';
    final file = File('${dir.path}/$fileName');
    await file.writeAsBytes(bytes);
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Saved to Downloads/$fileName')),
      );
    }
  } catch (e) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Export failed: $e')),
      );
    }
  }
}
