import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../../models/analytics_models.dart';

class StudyComparisonChart extends StatelessWidget {
  final List<CohortSeries> tumorData;
  final List<CohortSeries> weightData;

  const StudyComparisonChart({super.key, required this.tumorData, required this.weightData});

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
    return Column(
      children: [
        if (tumorData.isNotEmpty && tumorData.any((c) => c.series.isNotEmpty))
          _buildChart('Tumor Volume (mm³)', tumorData),
        const SizedBox(height: 16),
        if (weightData.isNotEmpty && weightData.any((c) => c.series.isNotEmpty))
          _buildChart('Body Weight (g)', weightData),
      ],
    );
  }

  Widget _buildChart(String title, List<CohortSeries> data) {
    final lineBars = <LineChartBarData>[];
    final legendItems = <Widget>[];

    for (var i = 0; i < data.length; i++) {
      final cohort = data[i];
      final color = _colors[i % _colors.length];
      final spots = cohort.series
          .map((p) => FlSpot(p.day.toDouble(), p.mean))
          .toList();

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
        Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        SizedBox(
          height: 200,
          child: LineChart(
            LineChartData(
              lineBarsData: lineBars,
              titlesData: FlTitlesData(
                bottomTitles: AxisTitles(
                  axisNameWidget: const Text('Day', style: TextStyle(fontSize: 11)),
                  sideTitles: SideTitles(showTitles: true, reservedSize: 28),
                ),
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 56,
                    getTitlesWidget: (value, meta) {
                      String text;
                      if (value >= 1000) {
                        text = '${(value / 1000).toStringAsFixed(1)}k';
                      } else if (value == value.roundToDouble()) {
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
        const SizedBox(height: 4),
        Wrap(spacing: 12, children: legendItems),
      ],
    );
  }
}
