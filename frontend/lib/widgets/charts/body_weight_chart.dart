import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../../models/analytics_models.dart';

class BodyWeightChart extends StatelessWidget {
  final List<CohortSeries> data;

  const BodyWeightChart({super.key, required this.data});

  static const _colors = [
    Colors.blue,
    Colors.red,
    Colors.green,
    Colors.orange,
    Colors.purple,
    Colors.teal,
  ];

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty || data.every((c) => c.series.isEmpty)) {
      return const Center(child: Text('No body weight data'));
    }

    final lineBars = <LineChartBarData>[];
    final betweenBars = <BetweenBarsData>[];
    final legendItems = <Widget>[];

    for (var i = 0; i < data.length; i++) {
      final cohort = data[i];
      final color = _colors[i % _colors.length];
      final spots = cohort.series
          .map((p) => FlSpot(p.day.toDouble(), p.mean))
          .toList();
      final upperSpots = cohort.series
          .map((p) => FlSpot(p.day.toDouble(), p.mean + p.sem))
          .toList();
      final lowerSpots = cohort.series
          .map((p) => FlSpot(p.day.toDouble(), (p.mean - p.sem).clamp(0, double.infinity)))
          .toList();

      final upperIdx = lineBars.length;
      lineBars.add(LineChartBarData(
        spots: upperSpots,
        isCurved: true,
        color: Colors.transparent,
        barWidth: 0,
        dotData: const FlDotData(show: false),
      ));

      final lowerIdx = lineBars.length;
      lineBars.add(LineChartBarData(
        spots: lowerSpots,
        isCurved: true,
        color: Colors.transparent,
        barWidth: 0,
        dotData: const FlDotData(show: false),
      ));

      betweenBars.add(BetweenBarsData(
        fromIndex: upperIdx,
        toIndex: lowerIdx,
        color: color.withAlpha(40),
      ));

      lineBars.add(LineChartBarData(
        spots: spots,
        isCurved: true,
        color: color,
        barWidth: 2,
        dotData: const FlDotData(show: true),
        belowBarData: BarAreaData(show: false),
      ));

      legendItems.add(Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 12, height: 12, color: color),
          const SizedBox(width: 4),
          Text(cohort.cohortName, style: const TextStyle(fontSize: 12)),
        ],
      ));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(bottom: 8),
          child: Text('Body Weight (mean \u00b1 SEM)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        ),
        SizedBox(
          height: 220,
          child: LineChart(
            LineChartData(
              lineBarsData: lineBars,
              betweenBarsData: betweenBars,
              titlesData: FlTitlesData(
                bottomTitles: AxisTitles(
                  axisNameWidget: const Text('Day', style: TextStyle(fontSize: 12)),
                  sideTitles: SideTitles(showTitles: true, reservedSize: 28),
                ),
                leftTitles: AxisTitles(
                  axisNameWidget: const Text('Weight (g)', style: TextStyle(fontSize: 12)),
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 56,
                    getTitlesWidget: (value, meta) {
                      String text;
                      if (value == value.roundToDouble()) {
                        text = value.toInt().toString();
                      } else {
                        text = value.toStringAsFixed(1);
                      }
                      return SideTitleWidget(meta: meta, child: Text(text, style: const TextStyle(fontSize: 10)));
                    },
                  ),
                ),
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              ),
              gridData: const FlGridData(show: true),
              borderData: FlBorderData(show: true),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Wrap(spacing: 16, children: legendItems),
      ],
    );
  }
}
