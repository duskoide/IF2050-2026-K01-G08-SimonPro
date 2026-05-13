import cProfile
import pstats
import io
from src.services.DashboardService import DashboardService
from src.services.LaporanService import LaporanService
from src.database.db_connection import get_db

def profile_features():
    print("Starting Performance Profiling...\n")
    
    # Initialize services
    dashboard_service = DashboardService()
    laporan_service = LaporanService()
    
    pr = cProfile.Profile()
    pr.enable()
    
    print("Profiling DashboardService.get_summary_data()...")
    for _ in range(10):  # Run multiple times to get better stats
        dashboard_service.get_summary_data()
        
    print("Profiling DashboardService.get_chart_data()...")
    for _ in range(10):
        dashboard_service.get_chart_data()
        
    print("Profiling LaporanService.get_html_preview()...")
    from datetime import date
    laporan_service.get_html_preview(date(2025, 1, 1), date(2025, 4, 30))
    
    pr.disable()
    
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(20) # Top 20 functions
    
    print("\n--- Profiling Results (Top 20 Cumulative Time) ---")
    print(s.getvalue())
    
    # Save to file
    with open("doc/performance_report.txt", "w") as f:
        f.write("SiMonPro Performance Profiling Report\n")
        f.write("=====================================\n\n")
        f.write(s.getvalue())
    print("\nReport saved to doc/performance_report.txt")

if __name__ == "__main__":
    profile_features()
