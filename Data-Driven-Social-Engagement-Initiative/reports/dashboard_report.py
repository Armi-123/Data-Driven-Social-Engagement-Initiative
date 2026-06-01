# reports/dashboard_report.py

import os
import tempfile
from datetime import datetime
from fpdf import FPDF


# ================= PDF CLASS =================
class PDF(FPDF):

    def header(self):
        if self.page_no() == 1:
            self.set_font("Helvetica", "", 18)
            self.cell(
                0, 14,
                "Data-Driven Social Engagement Analytics Report",
                ln=True, align="C"
            )

            self.set_font("Helvetica", "", 11)
            self.cell(
                0, 8,
                "Sentiment | Virality | Engagement | Trend Forecasting",
                ln=True, align="C"
            )

            self.set_font("Helvetica", "", 9)
            self.cell(
                0, 6,
                f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
                ln=True, align="C"
            )

            self.ln(10)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.cell(
            0, 10,
            f"Data-Driven Social Engagement Analytics System | Page {self.page_no()}",
            align="C"
        )


# ================= HELPERS =================
def section_title(pdf, title):
    pdf.set_fill_color(230, 238, 249)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, title, ln=True, fill=True)
    pdf.ln(6)


def executive_summary(df):
    total_posts = len(df)
    positive_pct = (df["sentiment_label"] == "positive").mean() * 100
    high_viral = (df["virality_label"] == "High").sum()
    avg_virality = df["virality_score"].mean()

    return (
        f"This report presents an analytical overview of social media engagement. "
        f"A total of {total_posts} posts were analyzed. "
        f"{positive_pct:.1f}% of posts show positive sentiment. "
        f"{high_viral} posts achieved high virality. "
        f"The average virality score is {avg_virality:.2f}."
    )


def kpi_table(pdf, df):
    metrics = [
        ("Total Posts", len(df)),
        ("Positive Sentiment (%)", f"{(df['sentiment_label']=='positive').mean()*100:.1f}%"),
        ("High Virality Posts", (df["virality_label"] == "High").sum()),
        ("Average Virality Score", f"{df['virality_score'].mean():.2f}"),
        ("Total Views", int(df["views"].sum())),
        ("Total Likes", int(df["likes"].sum())),
        ("Total Comments", int(df["comments"].sum())),
    ]

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(245, 245, 245)

    for k, v in metrics:
        pdf.cell(90, 9, k, border=1, fill=True)
        pdf.cell(60, 9, str(v), border=1)
        pdf.ln()

    pdf.ln(8)


def add_chart_page(pdf, title, fig):
    pdf.add_page()
    section_title(pdf, title)

    tmp_dir = tempfile.mkdtemp()
    img_path = os.path.join(tmp_dir, f"{title}.png")

    fig.write_image(img_path, scale=2)
    pdf.image(img_path, x=15, w=180)
    pdf.ln(10)


# ================= MAIN =================
def generate_dashboard_report(
    df,
    filters,
    charts,
    forecast_df,
    prepared_by
):

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ================= PAGE 1 =================
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)

    # Filters info
    for k, v in filters.items():
        pdf.cell(0, 6, f"{k}: {v}", ln=True)

    pdf.ln(6)

    # Executive Summary (NOT BOLD)
    section_title(pdf, "Executive Summary")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, executive_summary(df))

    pdf.ln(6)

    # ================= Key Insights =================
    section_title(pdf, "Key Insights")
    pdf.set_font("Helvetica", "", 11)

    positive_pct = (df["sentiment_label"] == "positive").mean() * 100
    neutral_pct = (df["sentiment_label"] == "neutral").mean() * 100
    avg_virality = df["virality_score"].mean()

    pdf.multi_cell(
        0, 8,
        f"- Neutral sentiment posts dominate volume ({neutral_pct:.1f}%).\n"
        f"- Positive sentiment posts contribute stronger engagement quality.\n"
        f"- Average virality score remains stable at {avg_virality:.2f}.\n"
        f"- Forecasting highlights mid-week as optimal for high-impact posting."
    )

    pdf.ln(6)


    # ================= PAGE 2 =================
    add_chart_page(pdf, "Sentiment Distribution", charts["sentiment"])

    # ================= PAGE 3 =================
    add_chart_page(pdf, "Virality vs Sentiment", charts["virality"])

    # ================= PAGE 4 =================
    add_chart_page(pdf, "Engagement Forecast", charts["forecast"])

    # ================= PAGE 5 =================
    pdf.add_page()
    section_title(pdf, "Forecast Insights")
    pdf.set_font("Helvetica", "", 11)

    if (
        forecast_df is not None
        and not forecast_df.empty
        and "predicted_engagement" in forecast_df.columns
    ):
        idx = forecast_df["predicted_engagement"].idxmax()

        peak_day = forecast_df.loc[idx, "date"].strftime("%d %B %Y")
        peak_value = int(forecast_df.loc[idx, "predicted_engagement"])

        pdf.multi_cell(
            0, 8,
            f"Based on historical engagement patterns, the forecasting model predicts "
            f"the highest audience interaction on {peak_day}, with approximately "
            f"{peak_value:,} interactions. Publishing high-impact or promotional "
            f"content on this day is strongly recommended to maximize engagement."
        )
    else:
        pdf.multi_cell(
            0, 8,
            "Forecast insights could not be generated because prediction data "
            "was unavailable or incomplete at the time of report generation."
        )



    # ================= PAGE 6 =================
    pdf.add_page(orientation="L")
    section_title(pdf, "Data Preview")

    preview = df.head(15)
    cols = ["video_id", "sentiment_label", "virality_score", "views", "likes", "comments"]
    col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / len(cols)

    pdf.set_font("Helvetica", "B", 9)
    for c in cols:
        pdf.cell(col_w, 8, c.upper(), border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for _, row in preview.iterrows():
        for c in cols:
            pdf.cell(col_w, 8, str(row[c]), border=1)
        pdf.ln()

    pdf.ln(8)
    pdf.cell(0, 6, f"Prepared by: Armi Sherathiya", ln=True)

    filename = f"Social_Engagement_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    reports_dir = os.path.join(os.getcwd(), "reports_output")
    os.makedirs(reports_dir, exist_ok=True)

    path = os.path.join(reports_dir, filename)
    pdf.output(path)

    return path
