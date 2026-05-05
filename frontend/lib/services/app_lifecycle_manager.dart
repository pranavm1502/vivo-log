import 'package:flutter/material.dart';

import 'backend_lifecycle.dart';
import 'database_lifecycle.dart';

/// Orchestrates startup and shutdown of the embedded database and backend.
class AppLifecycleManager with WidgetsBindingObserver {
  final DatabaseLifecycle _db = DatabaseLifecycle();
  final BackendLifecycle _backend = BackendLifecycle();

  bool _started = false;

  /// Start all services. Returns when the backend is ready.
  Future<void> start() async {
    if (_started) return;

    await _db.start();
    await _backend.start();
    _started = true;

    WidgetsBinding.instance.addObserver(this);
  }

  /// Stop all services gracefully.
  Future<void> stop() async {
    if (!_started) return;
    WidgetsBinding.instance.removeObserver(this);
    await _backend.stop();
    await _db.stop();
    _started = false;
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.detached) {
      stop();
    }
  }
}
