import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as p;

/// Manages the lifecycle of the bundled PostgreSQL server.
///
/// On first launch, runs `initdb` to create the data directory.
/// Starts postgres on port 5433 and stops it on shutdown.
class DatabaseLifecycle {
  Process? _process;
  final int port;

  DatabaseLifecycle({this.port = 5433});

  String get _appSupportDir {
    final home = Platform.environment['HOME'] ?? '/tmp';
    return p.join(home, 'Library', 'Application Support', 'Vivo-Log');
  }

  String get _dataDir => p.join(_appSupportDir, 'db');
  String get _logDir => p.join(_appSupportDir, 'logs');

  String get _pgDir {
    if (kDebugMode) {
      // In debug mode, use the packaging directory from the repo
      return p.join(Directory.current.path, '..', 'packaging', 'postgres');
    }
    // In release mode, use the bundled postgres inside the .app
    final executable = Platform.resolvedExecutable;
    final appBundle = p.dirname(p.dirname(executable)); // Contents/MacOS -> Contents
    return p.join(appBundle, 'Resources', 'postgres');
  }

  String get _pgBin => p.join(_pgDir, 'bin');
  String get _pgLib => p.join(_pgDir, 'lib');
  String get _pgShare => p.join(_pgDir, 'share');

  /// Start PostgreSQL, initializing the database on first run.
  Future<void> start() async {
    await Directory(_logDir).create(recursive: true);

    // Clean up any running postgres from a previous session
    await _stopExisting();

    // Initialize database if needed
    if (!Directory(_dataDir).existsSync() ||
        !File(p.join(_dataDir, 'PG_VERSION')).existsSync()) {
      await _initDb();
    }

    // Start postgres
    _process = await Process.start(
      p.join(_pgBin, 'postgres'),
      ['-D', _dataDir, '-p', port.toString(), '-k', '', '-h', '127.0.0.1'],
      environment: {'DYLD_LIBRARY_PATH': _pgLib, 'LC_ALL': 'C'},
    );

    // Log output
    final logFile = File(p.join(_logDir, 'postgres.log'));
    _process!.stdout.pipe(logFile.openWrite(mode: FileMode.append));
    _process!.stderr.pipe(logFile.openWrite(mode: FileMode.append));

    // Wait for postgres to be ready
    await _waitForReady();
  }

  /// Stop any existing postgres using pg_ctl for clean shared memory release.
  Future<void> _stopExisting() async {
    if (!Directory(_dataDir).existsSync()) return;
    final pidFile = File(p.join(_dataDir, 'postmaster.pid'));
    if (!pidFile.existsSync()) return;

    // Use pg_ctl stop for a clean shutdown (releases shared memory)
    await Process.run(
      p.join(_pgBin, 'pg_ctl'),
      ['stop', '-D', _dataDir, '-m', 'fast', '-w'],
      environment: {'DYLD_LIBRARY_PATH': _pgLib, 'LC_ALL': 'C'},
    );
    // Give shared memory a moment to be released
    await Future.delayed(const Duration(seconds: 1));

    // If PID file still exists, force kill
    if (pidFile.existsSync()) {
      final pidContent = pidFile.readAsStringSync();
      final pid = int.tryParse(pidContent.split('\n').first.trim());
      if (pid != null) {
        try {
          Process.killPid(pid, ProcessSignal.sigkill);
        } catch (_) {}
      }
      try {
        pidFile.deleteSync();
      } catch (_) {}
      await Future.delayed(const Duration(seconds: 1));
    }
  }

  Future<void> _initDb() async {
    await Directory(_dataDir).create(recursive: true);
    final result = await Process.run(
      p.join(_pgBin, 'initdb'),
      [
        '--pgdata=$_dataDir',
        '--encoding=UTF8',
        '--username=postgres',
        '--auth=trust',
        '-L', _pgShare,
      ],
      environment: {'DYLD_LIBRARY_PATH': _pgLib, 'LC_ALL': 'C'},
    );
    if (result.exitCode != 0) {
      throw Exception('initdb failed: ${result.stderr}');
    }
  }

  Future<void> _waitForReady() async {
    final pgIsReady = p.join(_pgBin, 'pg_isready');
    for (var i = 0; i < 30; i++) {
      final result = await Process.run(
        pgIsReady,
        ['-h', '127.0.0.1', '-p', port.toString()],
        environment: {'DYLD_LIBRARY_PATH': _pgLib, 'LC_ALL': 'C'},
      );
      if (result.exitCode == 0) return;
      await Future.delayed(const Duration(milliseconds: 500));
    }
    throw Exception('PostgreSQL failed to start within 15 seconds');
  }

  /// Create the vivolog database if it doesn't exist.
  /// Note: The backend handles this via run_server.py on startup.

  /// Stop PostgreSQL gracefully using pg_ctl.
  Future<void> stop() async {
    // Use pg_ctl for clean shutdown (properly releases shared memory)
    if (Directory(_dataDir).existsSync()) {
      await Process.run(
        p.join(_pgBin, 'pg_ctl'),
        ['stop', '-D', _dataDir, '-m', 'fast', '-w'],
        environment: {'DYLD_LIBRARY_PATH': _pgLib, 'LC_ALL': 'C'},
      );
    }
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
