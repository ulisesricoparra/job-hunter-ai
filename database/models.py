import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


class Job(Base):
    """Modelo ORM para la tabla 'jobs'."""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa = Column(String(255), nullable=False)
    puesto = Column(String(255), nullable=False)
    salario = Column(String(100), default="No especificado")
    modalidad = Column(String(100), default="No especificada")  # ej. Remote, On-site, Hybrid
    ubicacion = Column(String(255), default="No especificada")
    descripcion = Column(Text, nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    fuente = Column(String(100), nullable=False)  # ej. Indeed, GetOnBoard, RemoteOK
    fecha_publicacion = Column(String(100), default="")
    fecha_guardado = Column(DateTime, default=datetime.utcnow)

    # Campos para Fase 3 y 4 (Compatibilidad e IA)
    compatibilidad = Column(Float, default=0.0)
    estado = Column(String(50), default="Pendiente")  # Pendiente, Aplicada, Descartada
    analisis_ia = Column(Text, default="")

    __table_args__ = (
        UniqueConstraint('empresa', 'puesto', 'fuente', name='uix_empresa_puesto_fuente'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Job a un diccionario."""
        return {
            "id": self.id,
            "empresa": self.empresa,
            "puesto": self.puesto,
            "salario": self.salario,
            "modalidad": self.modalidad,
            "ubicacion": self.ubicacion,
            "descripcion": self.descripcion,
            "url": self.url,
            "fuente": self.fuente,
            "fecha_publicacion": self.fecha_publicacion,
            "compatibilidad": self.compatibilidad,
            "estado": self.estado
        }


class DatabaseManager:
    """Clase para la gestión y persistencia de vacantes en SQLite."""

    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def save_job(self, job_data: Dict[str, Any]) -> bool:
        """
        Inserta una nueva vacante si no existe previamente (basado en la URL o empresa+puesto+fuente).
        Devuelve True si fue insertada, False si era duplicada.
        """
        session: Session = self.SessionLocal()
        try:
            # Verificar por URL
            existing = session.query(Job).filter(Job.url == job_data.get("url")).first()
            if existing:
                return False

            new_job = Job(
                empresa=job_data.get("empresa", "Desconocida"),
                puesto=job_data.get("puesto", "Sin título"),
                salario=job_data.get("salario", "No especificado"),
                modalidad=job_data.get("modalidad", "No especificada"),
                ubicacion=job_data.get("ubicacion", "No especificada"),
                descripcion=job_data.get("descripcion", ""),
                url=job_data.get("url", ""),
                fuente=job_data.get("fuente", "Desconocida"),
                fecha_publicacion=job_data.get("fecha_publicacion", "")
            )
            session.add(new_job)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al guardar vacante: {e}")
            return False
        finally:
            session.close()

    def get_all_jobs(self) -> List[Job]:
        """Obtiene todas las vacantes guardadas."""
        session: Session = self.SessionLocal()
        try:
            return session.query(Job).all()
        finally:
            session.close()

    def update_job_compatibility(self, job_id: int, score: float, status: str = "Pendiente"):
        """Actualiza la puntuación de compatibilidad de una vacante por su ID."""
        session: Session = self.SessionLocal()
        try:
            job = session.query(Job).filter(Job.id == job_id).first()
            if job:
                job.compatibilidad = score
                job.estado = status
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar compatibilidad: {e}")
            return False
        finally:
            session.close()