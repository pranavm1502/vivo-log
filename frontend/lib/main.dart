import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/dashboard/dashboard_screen.dart';
import 'screens/colony/mouse_list_screen.dart';
import 'screens/colony/cage_list_screen.dart';
import 'screens/study/study_list_screen.dart';
import 'services/app_lifecycle_manager.dart';

final _lifecycleManager = AppLifecycleManager();

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: VivoLogApp()));
}

class VivoLogApp extends StatelessWidget {
  const VivoLogApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Vivo-Log',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: kDebugMode ? const HomeScreen() : const _StartupScreen(),
    );
  }
}

/// Shows a loading indicator while starting the embedded database and backend.
class _StartupScreen extends StatefulWidget {
  const _StartupScreen();

  @override
  State<_StartupScreen> createState() => _StartupScreenState();
}

class _StartupScreenState extends State<_StartupScreen> {
  String _status = 'Starting database...';
  bool _failed = false;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _startServices();
  }

  Future<void> _startServices() async {
    try {
      setState(() => _status = 'Starting database...');
      await _lifecycleManager.start();
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _failed = true;
          _error = e.toString();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: _failed
            ? Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  const Text('Failed to start services', style: TextStyle(fontSize: 18)),
                  const SizedBox(height: 8),
                  Text(_error, style: const TextStyle(color: Colors.grey)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      setState(() { _failed = false; });
                      _startServices();
                    },
                    child: const Text('Retry'),
                  ),
                ],
              )
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  Text(_status, style: const TextStyle(fontSize: 16)),
                ],
              ),
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  static const _screens = <Widget>[
    DashboardScreen(),
    MouseListScreen(),
    CageListScreen(),
    StudyListScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (i) => setState(() => _selectedIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.pets), label: 'Mice'),
          NavigationDestination(icon: Icon(Icons.grid_view), label: 'Cages'),
          NavigationDestination(icon: Icon(Icons.science), label: 'Studies'),
        ],
      ),
    );
  }
}
