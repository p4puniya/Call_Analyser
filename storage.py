import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from models import CallAnalysisResponse

# Configure logging
logger = logging.getLogger(__name__)

# Storage configuration
DATA_DIR = Path("data")
ANALYSIS_FILE = DATA_DIR / "analyzed_calls.json"
METADATA_FILE = DATA_DIR / "analysis_metadata.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def load_data() -> List[Dict[str, Any]]:
    """
    Load all analysis data from storage
    """
    try:
        if ANALYSIS_FILE.exists():
            with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} analysis records from storage")
                return data
        else:
            logger.info("No analysis data found, starting with empty storage")
            return []
    except Exception as e:
        logger.error(f"Error loading analysis data: {str(e)}")
        return []

def save_analysis(analysis_result: Dict[str, Any]) -> bool:
    """
    Save a single analysis result to storage
    
    Args:
        analysis_result: Dictionary containing the analysis result
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Ensure the result has a timestamp
        if "timestamp" not in analysis_result:
            analysis_result["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Load existing data
        data = load_data()
        
        # Add the new analysis
        data.append(analysis_result)
        
        # Save back to file
        with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved analysis for call {analysis_result.get('call_id', 'unknown')}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving analysis: {str(e)}")
        return False

def save_batch_analyses(analyses: List[Dict[str, Any]]) -> bool:
    """
    Save multiple analysis results to storage
    
    Args:
        analyses: List of analysis result dictionaries
        
    Returns:
        bool: True if all saved successfully, False otherwise
    """
    try:
        # Load existing data
        data = load_data()
        
        # Add timestamps to new analyses
        current_time = datetime.now(timezone.utc).isoformat()
        for analysis in analyses:
            if "timestamp" not in analysis:
                analysis["timestamp"] = current_time
        
        # Add all new analyses
        data.extend(analyses)
        
        # Save back to file
        with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(analyses)} analysis records to storage")
        return True
        
    except Exception as e:
        logger.error(f"Error saving batch analyses: {str(e)}")
        return False

def get_analysis_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    call_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get analysis history with optional filtering
    
    Args:
        start_date: ISO format date string (e.g., "2024-01-01T00:00:00Z")
        end_date: ISO format date string (e.g., "2024-12-31T23:59:59Z")
        call_id: Filter by specific call ID
        status: Filter by analysis status ("analyzed", "skipped", "error")
        limit: Maximum number of results to return
        
    Returns:
        List of filtered analysis records
    """
    try:
        data = load_data()
        
        # Apply filters
        filtered_data = data
        
        # Filter by date range
        if start_date or end_date:
            filtered_data = _filter_by_date_range(filtered_data, start_date, end_date)
        
        # Filter by call ID
        if call_id:
            filtered_data = [item for item in filtered_data if item.get("call_id") == call_id]
        
        # Filter by status
        if status:
            filtered_data = [item for item in filtered_data if item.get("status") == status]
        
        # Apply limit
        if limit and limit > 0:
            filtered_data = filtered_data[:limit]
        
        # Sort by timestamp (newest first)
        filtered_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        logger.info(f"Retrieved {len(filtered_data)} analysis records with filters")
        return filtered_data
        
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        return []

def _filter_by_date_range(
    data: List[Dict[str, Any]], 
    start_date: Optional[str], 
    end_date: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Filter data by date range
    """
    try:
        filtered = []
        
        for item in data:
            timestamp = item.get("timestamp")
            if not timestamp:
                continue
                
            # Parse timestamp
            try:
                item_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                # Try parsing without timezone info
                item_dt = datetime.fromisoformat(timestamp)
            
            # Apply start date filter
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                except ValueError:
                    start_dt = datetime.fromisoformat(start_date)
                if item_dt < start_dt:
                    continue
            
            # Apply end date filter
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                except ValueError:
                    end_dt = datetime.fromisoformat(end_date)
                if item_dt > end_dt:
                    continue
            
            filtered.append(item)
        
        return filtered
        
    except Exception as e:
        logger.error(f"Error filtering by date range: {str(e)}")
        return data

def get_analysis_stats() -> Dict[str, Any]:
    """
    Get statistics about stored analysis data
    """
    try:
        data = load_data()
        
        if not data:
            return {
                "total_analyses": 0,
                "date_range": None,
                "status_breakdown": {},
                "call_ids": []
            }
        
        # Calculate statistics
        total = len(data)
        status_counts = {}
        call_ids = set()
        timestamps = []
        
        for item in data:
            status = item.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            call_id = item.get("call_id")
            if call_id:
                call_ids.add(call_id)
            
            timestamp = item.get("timestamp")
            if timestamp:
                timestamps.append(timestamp)
        
        # Calculate date range
        date_range = None
        if timestamps:
            try:
                dates = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
                min_date = min(dates)
                max_date = max(dates)
                date_range = {
                    "earliest": min_date.isoformat(),
                    "latest": max_date.isoformat(),
                    "span_days": (max_date - min_date).days
                }
            except Exception as e:
                logger.warning(f"Error calculating date range: {str(e)}")
        
        return {
            "total_analyses": total,
            "date_range": date_range,
            "status_breakdown": status_counts,
            "unique_calls": len(call_ids),
            "call_ids": list(call_ids)[:10]  # First 10 for preview
        }
        
    except Exception as e:
        logger.error(f"Error calculating analysis stats: {str(e)}")
        return {"error": str(e)}

def clear_analysis_data() -> bool:
    """
    Clear all analysis data (use with caution!)
    """
    try:
        if ANALYSIS_FILE.exists():
            ANALYSIS_FILE.unlink()
            logger.info("Cleared all analysis data")
        return True
    except Exception as e:
        logger.error(f"Error clearing analysis data: {str(e)}")
        return False

def backup_analysis_data(backup_path: Optional[str] = None) -> bool:
    """
    Create a backup of analysis data
    
    Args:
        backup_path: Optional custom backup path
        
    Returns:
        bool: True if backup successful, False otherwise
    """
    try:
        if not ANALYSIS_FILE.exists():
            logger.warning("No analysis data to backup")
            return False
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = DATA_DIR / f"analyzed_calls_backup_{timestamp}.json"
        else:
            backup_path = Path(backup_path)
        
        # Copy the file
        import shutil
        shutil.copy2(ANALYSIS_FILE, backup_path)
        
        logger.info(f"Backup created at: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        return False 