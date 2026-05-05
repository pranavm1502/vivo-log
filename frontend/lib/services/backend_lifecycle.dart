import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as p;

/// Manages the lifecycle of the bundled FastAPI backend server.
///
/// Spawns the PyInstaller-compiled backend as a child process
/// and stops it on app shutdown.
class BackendLifecycle {
  Process? _process;
  final int port;
  final int dbPort;

  BackendLifecycle({this.port = 8000, this.dbPort = 5433});

  String get _backendPath {
    if (kDebugMode) {
      // In debug mode, use the dist from the repo
      return p.join(Directory.current.path, '..', 'backend', 'dist', 'backend', 'backend');
    }
    // In release mode, use the bundled backend inside the .app
    final executable = Platform.resolvedExecutable;
    final appBundle = p.dirname(p.dirname(executable)); // Contents/MacOS -> Contents
    return p.join(appBundle, 'Resources', 'backend', 'backend');
  }

  String get _logDir {
    final home = Platform.environment['HOME'] ?? '/tmp';
    return p.join(home, 'Library', 'Application Support', 'Vivo-Log', 'logs');
  }

  /// Start the backend server.
  Future<void> start() async {
    await Directory(_logDir).create(recursive: true);

    final dbUrl = 'postgresql+asyncpg://postgres:@127.0.0.1:$dbPort/vivolog';
    final dbUrlSync = 'postgresql://postgres:@127.0.0.1:$dbPort/vivolog';

    _process = await Process.start(
      _backendPath,
      [],
      environment: {
        'VIVOLOG_DATABASE_URL': dbUrl,
        'VIVOLOG_DATABASE_URL_SYNC': dbUrlSync,
        'VIVOLOG_HOST': '127.0.0.1',
        'VIVOLOG_PORT': port.toString(),
      },
    );

    // Log output
    final logFile = File(p.join(_logDir, 'backend.log'));
    _process!.stdout.pipe(logFile.openWrite(mode: FileMode.append));
    _process!.stderr.pipe(logFile.openWrite(mode: FileMode.append));

    // Wait for the backend to be ready
    await _waitForReady();
  }

  Future<void> _waitForReady() async {
    final client = HttpClient();
    for (var i = 0; i < 30; i++) {
      try {
        final request = await client.get('127.0.0.1', port, '/docs');
        final response = await request.close();
        if (response.statusCode == 200) {
          client.close();
          return;
        }
      } catch (_) {}
      await Future.delayed(const Duration(milliseconds: 500));
    }
    client.close();
    throw Exception('Backend failed to start within 15 seconds');
  }

  /// Stop the backend server gracefully.
  Future<void> stop() async {
    if (_process != null) {
      _process!.kill(ProcessSignal.sigterm);
      await _process!.exitCode.timeout(
        const Duration(seconds: 5),
        onTimeout: () {
          _process!.kill(ProcessSignal.sigkill);
          return -1;
        },
      );
      _process = null;
    }
  }
}
