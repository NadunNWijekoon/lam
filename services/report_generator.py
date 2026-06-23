import os
import csv
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# ReportLab Imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from database.db_manager import DBManager
from config import EXPORTS_DIR, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_CARD_BG

class ReportGenerator:
    def __init__(self):
        self.db = DBManager()

    def generate_csv(self, filename="traffic_report.csv"):
        """Export historical statistics to CSV format."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        stats = self.db.get_latest_statistics(limit=1000)
        
        if not stats:
            return None, "No data available in database."

        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Index", "Active Vehicles", "Average Speed (km/h)", "Traffic Density (%)", "Timestamp"])
                for idx, row in enumerate(stats):
                    writer.writerow([
                        idx + 1,
                        row["vehicles_count"],
                        row["avg_speed"],
                        row["traffic_density"],
                        row["timestamp"]
                    ])
            return filepath, "CSV report successfully exported."
        except Exception as e:
            return None, f"Failed to export CSV: {str(e)}"

    def generate_excel(self, filename="traffic_report.xlsx"):
        """Export simulation logs and stats to a multi-sheet styled Excel file."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        stats = self.db.get_latest_statistics(limit=1000)
        events = self.db.get_all_events(limit=1000)
        
        if not stats:
            return None, "No simulation telemetry available."

        try:
            # Create DataFrames
            df_stats = pd.DataFrame(stats)
            df_stats.columns = ["Active Vehicles", "Average Speed (km/h)", "Traffic Density (%)", "Timestamp"]
            
            df_events = pd.DataFrame(events)
            if not df_events.empty:
                df_events.columns = ["Event Type", "Message/Location", "Timestamp", "Severity"]
            else:
                df_events = pd.DataFrame(columns=["Event Type", "Message/Location", "Timestamp", "Severity"])

            # Summary tab data
            summary_data = {
                "Metric": [
                    "Report Generation Time",
                    "Total Telemetry Logged",
                    "Max Active Vehicles Record",
                    "Average Traffic Density (%)",
                    "Total Events Recorded"
                ],
                "Value": [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    len(df_stats),
                    df_stats["Active Vehicles"].max() if not df_stats.empty else 0,
                    round(df_stats["Traffic Density (%)"].mean(), 2) if not df_stats.empty else 0.0,
                    len(df_events)
                ]
            }
            df_summary = pd.DataFrame(summary_data)

            # Export using pandas and openpyxl
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_summary.to_excel(writer, sheet_name="Summary", index=False)
                df_stats.to_excel(writer, sheet_name="Telemetry Ticks", index=False)
                df_events.to_excel(writer, sheet_name="Incident Logs", index=False)
                
            return filepath, "Excel report successfully exported with multiple tabs."
        except Exception as e:
            return None, f"Failed to export Excel: {str(e)}"

    def generate_pdf(self, filename="traffic_report.pdf"):
        """Generates a professional PDF containing graphs, statistics, and tables."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        stats = self.db.get_latest_statistics(limit=100)
        events = self.db.get_all_events(limit=15) # Show last 15 incidents
        
        if not stats:
            return None, "No simulation telemetry available."

        try:
            # Step 1: Save a temporary chart image using Matplotlib
            chart_path = os.path.join(EXPORTS_DIR, "temp_chart.png")
            self._create_pdf_chart(stats, chart_path)

            # Step 2: Build ReportLab Document
            doc = SimpleDocTemplate(
                filepath, 
                pagesize=letter,
                rightMargin=36, leftMargin=36,
                topMargin=36, bottomMargin=36
            )
            story = []
            
            # Setup Styles
            styles = getSampleStyleSheet()
            
            # Modify existing styles to avoid collisions
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=22,
                textColor=colors.HexColor(COLOR_PRIMARY),
                spaceAfter=6
            )
            subtitle_style = ParagraphStyle(
                'DocSubtitle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=11,
                textColor=colors.HexColor(COLOR_SECONDARY),
                spaceAfter=15
            )
            h2_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.HexColor('#222222'),
                spaceBefore=12,
                spaceAfter=8
            )
            body_style = ParagraphStyle(
                'DocBody',
                parent=styles['BodyText'],
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                spaceAfter=6
            )

            # Document Title
            story.append(Paragraph("LAM Simulation Platform", title_style))
            story.append(Paragraph(f"Real-Time Smart City Analytics Report — Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
            story.append(Spacer(1, 10))

            # Summary Table
            df_stats = pd.DataFrame(stats)
            avg_density = df_stats["traffic_density"].mean() if not df_stats.empty else 0
            max_vehicles = df_stats["vehicles_count"].max() if not df_stats.empty else 0
            avg_speed = df_stats["avg_speed"].mean() if not df_stats.empty else 0
            
            summary_table_data = [
                [Paragraph("<b>Key Metric</b>", body_style), Paragraph("<b>Value</b>", body_style)],
                [Paragraph("Total Telemetry Steps Analyzed", body_style), Paragraph(str(len(stats)), body_style)],
                [Paragraph("Average Smart City Traffic Density", body_style), Paragraph(f"{avg_density:.1f}%", body_style)],
                [Paragraph("Peak Spawned Active Vehicles", body_style), Paragraph(str(max_vehicles), body_style)],
                [Paragraph("Average Simulated Speed", body_style), Paragraph(f"{avg_speed:.1f} km/h", body_style)]
            ]
            
            t_summary = Table(summary_table_data, colWidths=[250, 200])
            t_summary.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ]))
            
            story.append(Paragraph("1. Executive Simulation Summary", h2_style))
            story.append(t_summary)
            story.append(Spacer(1, 15))

            # Add Chart Image
            if os.path.exists(chart_path):
                story.append(Paragraph("2. Real-Time Analytics Trend Plot", h2_style))
                story.append(Image(chart_path, width=6.5 * inch, height=3.2 * inch))
                story.append(Spacer(1, 15))

            # Event Logs Table
            story.append(Paragraph("3. Logged Smart City Incidents (Latest)", h2_style))
            
            event_table_headers = [
                Paragraph("<b>Time</b>", body_style), 
                Paragraph("<b>Event Type</b>", body_style), 
                Paragraph("<b>Details / Location</b>", body_style), 
                Paragraph("<b>Severity</b>", body_style)
            ]
            
            event_table_data = [event_table_headers]
            for ev in events:
                sev_color = '#000000'
                if ev["severity"] == "Critical":
                    sev_color = COLOR_DANGER
                elif ev["severity"] == "Warning":
                    sev_color = COLOR_WARNING
                else:
                    sev_color = COLOR_PRIMARY
                
                event_table_data.append([
                    Paragraph(ev["time"], body_style),
                    Paragraph(ev["event_type"], body_style),
                    Paragraph(ev["location"], body_style),
                    Paragraph(f"<font color='{sev_color}'><b>{ev['severity']}</b></font>", body_style)
                ])

            if len(event_table_data) > 1:
                t_events = Table(event_table_data, colWidths=[60, 90, 240, 60])
                t_events.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ]))
                story.append(t_events)
            else:
                story.append(Paragraph("No events logged during this run session.", body_style))

            # Build PDF
            doc.build(story)
            
            # Clean up temp image
            if os.path.exists(chart_path):
                os.remove(chart_path)
                
            return filepath, "PDF report containing embedded charts and statistics created."
            
        except Exception as e:
            return None, f"Failed to generate PDF: {str(e)}"

    def _create_pdf_chart(self, stats, output_path):
        """Helper to create and save a matplotlib chart for PDF reports."""
        times = [row["timestamp"] for row in stats]
        vehicles = [row["vehicles_count"] for row in stats]
        density = [row["traffic_density"] for row in stats]
        
        # Downsample labels for readability
        n_ticks = 10
        step = max(1, len(times) // n_ticks)
        tick_indices = list(range(0, len(times), step))
        tick_labels = [times[i] for i in tick_indices]

        plt.figure(figsize=(10, 5))
        
        # Plot Vehicles
        plt.subplot(1, 2, 1)
        plt.plot(vehicles, color=COLOR_PRIMARY, linewidth=2, label="Vehicles")
        plt.title("Vehicle Load Profile", fontsize=10, fontweight='bold')
        plt.xlabel("Timeline", fontsize=8)
        plt.ylabel("Active Vehicles", fontsize=8)
        plt.xticks(tick_indices, tick_labels, rotation=45, fontsize=7)
        plt.grid(True, linestyle='--', alpha=0.5)

        # Plot Density
        plt.subplot(1, 2, 2)
        plt.plot(density, color=COLOR_SECONDARY, linewidth=2, label="Density")
        plt.title("Grid Congestion Trend", fontsize=10, fontweight='bold')
        plt.xlabel("Timeline", fontsize=8)
        plt.ylabel("Density (%)", fontsize=8)
        plt.xticks(tick_indices, tick_labels, rotation=45, fontsize=7)
        plt.grid(True, linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
