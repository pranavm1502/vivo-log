import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/colony/mouse_list_screen.dart';
import 'screens/colony/cage_list_screen.dart';
import 'screens/study/study_list_screen.dart';

void main() {
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
      home: const HomeScreen(),
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
          NavigationDestination(icon: Icon(Icons.pets), label: 'Mice'),
          NavigationDestination(icon: Icon(Icons.grid_view), label: 'Cages'),
          NavigationDestination(icon: Icon(Icons.science), label: 'Studies'),
        ],
      ),
    );
  }
}
