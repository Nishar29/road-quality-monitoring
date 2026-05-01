"""
Database Models Module

SQLAlchemy ORM models for the Road Quality Monitoring System.
Includes models for road segments, readings, metrics, alerts, and users.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey, Enum, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    readings = relationship("Reading", back_populates="user")
    alerts_acknowledged = relationship("Alert", back_populates="acknowledged_by_user")

    def __repr__(self):
        return f"<User {self.email}>"


class RoadSegment(Base):
    """Road segment model representing a section of road."""
    __tablename__ = "road_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    length_km = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    highway_type = Column(String(100), nullable=False)  # Interstate, State, County, Local
    surface_type = Column(String(100), default="asphalt")  # asphalt, concrete, gravel
    speed_limit = Column(Integer, default=55)
    traffic_volume = Column(Integer, default=0)
    last_maintenance = Column(DateTime, nullable=True)
    maintenance_priority = Column(String(50), default="low")  # low, medium, high, critical
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    readings = relationship("Reading", back_populates="road_segment", cascade="all, delete-orphan")
    metrics = relationship("QualityMetric", back_populates="road_segment", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="road_segment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RoadSegment {self.name}>"


class SurfaceCondition(str, enum.Enum):
    """Enumeration for surface condition states."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very_poor"


class Reading(Base):
    """Road condition reading model."""
    __tablename__ = "readings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    device_id = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    surface_condition = Column(String(50), nullable=False)  # excellent, good, fair, poor, very_poor
    surface_type = Column(String(100), nullable=False)
    roughness_index = Column(Float, nullable=True)  # IRI - International Roughness Index
    pothole_count = Column(Integer, default=0)
    crack_extent = Column(Float, default=0.0)  # Percentage of surface
    pavement_distress = Column(Float, default=0.0)
    rutting_depth = Column(Float, nullable=True)
    texture_depth = Column(Float, nullable=True)
    additional_notes = Column(Text, nullable=True)
    sensor_data = Column(JSON, nullable=True)  # For storing raw sensor data
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    road_segment = relationship("RoadSegment", back_populates="readings")
    user = relationship("User", back_populates="readings")

    def __repr__(self):
        return f"<Reading {self.id} - {self.segment_id}>"


class QualityMetric(Base):
    """Road quality metrics model."""
    __tablename__ = "quality_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=False, index=True)
    calculation_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    road_condition_index = Column(Float, nullable=False)  # 0-100, higher is better
    pavement_condition_index = Column(Float, nullable=False)  # 0-100
    roughness_severity = Column(String(50), nullable=False)  # low, medium, high
    distress_severity = Column(String(50), nullable=False)  # low, medium, high
    trend = Column(String(50), nullable=False)  # improving, stable, deteriorating
    average_roughness = Column(Float, nullable=True)
    average_pothole_count = Column(Float, nullable=True)
    average_crack_extent = Column(Float, nullable=True)
    maintenance_recommended = Column(Boolean, default=False)
    estimated_maintenance_cost = Column(Float, nullable=True)
    readings_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    road_segment = relationship("RoadSegment", back_populates="metrics")

    def __repr__(self):
        return f"<QualityMetric {self.segment_id} - {self.calculation_date}>"


class AlertType(str, enum.Enum):
    """Enumeration for alert types."""
    POTHOLE_DETECTED = "pothole_detected"
    EXCESSIVE_CRACKING = "excessive_cracking"
    HIGH_ROUGHNESS = "high_roughness"
    RUTTING_DETECTED = "rutting_detected"
    MAINTENANCE_DUE = "maintenance_due"
    SEVERE_DETERIORATION = "severe_deterioration"
    UNUSUAL_PATTERN = "unusual_pattern"


class AlertSeverity(str, enum.Enum):
    """Enumeration for alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(Base):
    """Alert model for road condition issues."""
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # pothole, cracking, roughness, deterioration
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    status = Column(String(50), default="open")  # open, acknowledged, resolved, ignored
    acknowledged_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledgment_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    road_segment = relationship("RoadSegment", back_populates="alerts")
    acknowledged_by_user = relationship("User", back_populates="alerts_acknowledged")

    def __repr__(self):
        return f"<Alert {self.alert_type} - {self.severity}>"


class Report(Base):
    """Report model for generated analysis reports."""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=True, index=True)
    report_type = Column(String(100), nullable=False)  # segment_analysis, network_analysis, trend_analysis
    format = Column(String(50), nullable=False)  # pdf, csv, json
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")  # pending, generating, completed, failed
    file_path = Column(String(500), nullable=True)
    file_size_mb = Column(Float, nullable=True)
    generated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Report {self.report_type} - {self.id}>"


class MaintenanceSchedule(Base):
    """Maintenance schedule model."""
    __tablename__ = "maintenance_schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(100), nullable=False)  # patching, resurfacing, reconstruction
    estimated_cost = Column(Float, nullable=False)
    priority = Column(String(50), nullable=False)  # low, medium, high, critical
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MaintenanceSchedule {self.segment_id} - {self.scheduled_date}>"
