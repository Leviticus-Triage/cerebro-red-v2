"""
backend/api/results.py
======================

Experiment results and export endpoints for CEREBRO-RED v2 API.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
import csv
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from core.database import get_session, ExperimentRepository, AttackIterationRepository, VulnerabilityRepository
from core.models import ExperimentConfig
from api.auth import verify_api_key
from api.exceptions import ExperimentNotFoundException
from api.responses import api_response

router = APIRouter()


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/{experiment_id}", dependencies=[Depends(verify_api_key)])
async def get_experiment_results(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get complete experiment results including all iterations and vulnerabilities.
    """
    # Get experiment
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get iterations
    iteration_repo = AttackIterationRepository(session)
    iterations = await iteration_repo.get_by_experiment(experiment_id)
    
    # Get vulnerabilities
    vuln_repo = VulnerabilityRepository(session)
    vulnerabilities = await vuln_repo.get_by_experiment(experiment_id)
    
    # Calculate statistics
    total_iterations = len(iterations)
    successful_iterations = [it for it in iterations if it.success]
    success_rate = len(successful_iterations) / total_iterations if total_iterations > 0 else 0.0
    
    return api_response({
        "experiment_id": str(experiment_id),
        "experiment": {
            "name": experiment.name,
            "description": experiment.description,
            "status": experiment.status,
            "created_at": experiment.created_at.isoformat(),
            "max_iterations": experiment.max_iterations,
            "success_threshold": experiment.success_threshold
        },
        "iterations": [
            {
                "iteration_id": str(it.iteration_id),
                "iteration_number": it.iteration_number,
                "strategy_used": it.strategy_used,
                "original_prompt": it.original_prompt,
                "mutated_prompt": it.mutated_prompt,
                "target_response": it.target_response,
                "judge_score": it.judge_score,
                "judge_reasoning": it.judge_reasoning,
                "success": it.success,
                "latency_ms": it.latency_ms,
                "timestamp": it.timestamp.isoformat() if it.timestamp else None
            }
            for it in iterations
        ],
        "vulnerabilities": [
            {
                "vulnerability_id": str(v.vulnerability_id),
                "severity": v.severity,
                "title": v.title,
                "description": v.description,
                "attack_strategy": v.attack_strategy,
                "iteration_number": v.iteration_number,
                "judge_score": v.judge_score,
                "discovered_at": v.discovered_at.isoformat() if v.discovered_at else None
            }
            for v in vulnerabilities
        ],
        "statistics": {
            "total_iterations": total_iterations,
            "successful_iterations": len(successful_iterations),
            "success_rate": success_rate,
            "vulnerabilities_found": len(vulnerabilities)
        }
    })


@router.get("/{experiment_id}/summary", dependencies=[Depends(verify_api_key)])
async def get_experiment_summary(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get compact experiment result summary.
    """
    # Get experiment
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get iterations
    iteration_repo = AttackIterationRepository(session)
    iterations = await iteration_repo.get_by_experiment(experiment_id)
    
    # Get vulnerabilities
    vuln_repo = VulnerabilityRepository(session)
    vulnerabilities = await vuln_repo.get_by_experiment(experiment_id)
    
    # Calculate summary statistics
    total_iterations = len(iterations)
    successful_iterations = len([it for it in iterations if it.success])
    success_rate = successful_iterations / total_iterations if total_iterations > 0 else 0.0
    
    severity_counts = {
        "critical": len([v for v in vulnerabilities if v.severity == "critical"]),
        "high": len([v for v in vulnerabilities if v.severity == "high"]),
        "medium": len([v for v in vulnerabilities if v.severity == "medium"]),
        "low": len([v for v in vulnerabilities if v.severity == "low"])
    }
    
    return api_response({
        "experiment_id": str(experiment_id),
        "name": experiment.name,
        "status": experiment.status,
        "success_rate": success_rate,
        "total_iterations": total_iterations,
        "vulnerabilities_count": len(vulnerabilities),
        "vulnerabilities_by_severity": severity_counts,
        "created_at": experiment.created_at.isoformat()
    })


@router.get("/{experiment_id}/export", dependencies=[Depends(verify_api_key)])
async def export_experiment_results(
    experiment_id: UUID,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    include_prompts: bool = Query(True),
    include_responses: bool = Query(True),
    session: AsyncSession = Depends(get_session)
):
    """
    Export experiment results in specified format (JSON, CSV, or PDF).
    """
    # Get experiment
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get iterations
    iteration_repo = AttackIterationRepository(session)
    iterations = await iteration_repo.get_by_experiment(experiment_id)
    
    # Get vulnerabilities
    vuln_repo = VulnerabilityRepository(session)
    vulnerabilities = await vuln_repo.get_by_experiment(experiment_id)
    
    if format == "json":
        # JSON export
        data = {
            "experiment_id": str(experiment_id),
            "experiment": {
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status,
                "created_at": experiment.created_at.isoformat()
            },
            "iterations": [
                {
                    "iteration_number": it.iteration_number,
                    "strategy_used": it.strategy_used,
                    "original_prompt": it.original_prompt if include_prompts else None,
                    "mutated_prompt": it.mutated_prompt if include_prompts else None,
                    "target_response": it.target_response if include_responses else None,
                    "judge_score": it.judge_score,
                    "success": it.success
                }
                for it in iterations
            ],
            "vulnerabilities": [
                {
                    "vulnerability_id": str(v.vulnerability_id),
                    "severity": v.severity,
                    "title": v.title,
                    "description": v.description,
                    "attack_strategy": v.attack_strategy,
                    "iteration_number": v.iteration_number
                }
                for v in vulnerabilities
            ]
        }
        
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}.json"}
        )
    
    elif format == "csv":
        # CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = ["iteration_number", "strategy", "judge_score", "success"]
        if include_prompts:
            header.extend(["original_prompt", "mutated_prompt"])
        if include_responses:
            header.append("target_response")
        writer.writerow(header)
        
        # Write iterations
        for it in iterations:
            row = [it.iteration_number, it.strategy_used, it.judge_score, it.success]
            if include_prompts:
                row.extend([it.original_prompt, it.mutated_prompt])
            if include_responses:
                row.append(it.target_response)
            writer.writerow(row)
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}.csv"}
        )
    
    elif format == "pdf":
        # PDF export using reportlab
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Experiment Results Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Experiment Information
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12
            )
            story.append(Paragraph(f"<b>Experiment Name:</b> {experiment.name}", info_style))
            if experiment.description:
                story.append(Paragraph(f"<b>Description:</b> {experiment.description}", info_style))
            story.append(Paragraph(f"<b>Experiment ID:</b> {str(experiment_id)}", info_style))
            story.append(Paragraph(f"<b>Status:</b> {experiment.status}", info_style))
            story.append(Paragraph(f"<b>Created:</b> {experiment.created_at.strftime('%Y-%m-%d %H:%M:%S')}", info_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Statistics Summary
            total_iterations = len(iterations)
            successful_iterations = [it for it in iterations if it.success]
            success_rate = len(successful_iterations) / total_iterations if total_iterations > 0 else 0.0
            avg_score = sum(it.judge_score for it in iterations) / total_iterations if total_iterations > 0 else 0.0
            
            summary_style = ParagraphStyle(
                'SummaryStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#059669'),
                spaceAfter=15
            )
            story.append(Paragraph("Summary Statistics", summary_style))
            
            summary_data = [
                ["Metric", "Value"],
                ["Total Iterations", str(total_iterations)],
                ["Successful Iterations", str(len(successful_iterations))],
                ["Success Rate", f"{success_rate:.1%}"],
                ["Average Judge Score", f"{avg_score:.2f}"],
                ["Vulnerabilities Found", str(len(vulnerabilities))]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Iterations Table
            if iterations:
                iterations_style = ParagraphStyle(
                    'IterationsStyle',
                    parent=styles['Heading2'],
                    fontSize=16,
                    textColor=colors.HexColor('#059669'),
                    spaceAfter=15
                )
                story.append(Paragraph("Iterations", iterations_style))
                
                # Prepare table data
                iter_data = [["#", "Strategy", "Judge Score", "Success"]]
                for it in iterations[:50]:  # Limit to first 50 iterations for PDF
                    iter_data.append([
                        str(it.iteration_number),
                        it.strategy_used[:30] + "..." if len(it.strategy_used) > 30 else it.strategy_used,
                        f"{it.judge_score:.2f}",
                        "✓" if it.success else "✗"
                    ])
                
                if len(iterations) > 50:
                    iter_data.append(["...", f"({len(iterations) - 50} more iterations)", "", ""])
                
                iter_table = Table(iter_data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 1*inch])
                iter_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (2, 1), (2, -1), 'CENTER'),
                    ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(iter_table)
                story.append(Spacer(1, 0.3*inch))
            
            # Vulnerabilities Section
            if vulnerabilities:
                vuln_style = ParagraphStyle(
                    'VulnStyle',
                    parent=styles['Heading2'],
                    fontSize=16,
                    textColor=colors.HexColor('#dc2626'),
                    spaceAfter=15
                )
                story.append(Paragraph("Vulnerabilities Found", vuln_style))
                
                for v in vulnerabilities:
                    severity_color = {
                        'critical': colors.HexColor('#dc2626'),
                        'high': colors.HexColor('#ea580c'),
                        'medium': colors.HexColor('#f59e0b'),
                        'low': colors.HexColor('#84cc16')
                    }.get(v.severity.lower(), colors.black)
                    
                    vuln_title_style = ParagraphStyle(
                        'VulnTitle',
                        parent=styles['Heading3'],
                        fontSize=12,
                        textColor=severity_color,
                        spaceAfter=6
                    )
                    story.append(Paragraph(f"[{v.severity.upper()}] {v.title}", vuln_title_style))
                    
                    desc_style = ParagraphStyle(
                        'VulnDesc',
                        parent=styles['Normal'],
                        fontSize=10,
                        spaceAfter=12,
                        leftIndent=20
                    )
                    story.append(Paragraph(f"Strategy: {v.attack_strategy} | Iteration: {v.iteration_number}", desc_style))
                    if v.description:
                        story.append(Paragraph(v.description[:500] + ("..." if len(v.description) > 500 else ""), desc_style))
                    story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return Response(
                content=buffer.getvalue(),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}.pdf"}
            )
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF export requires reportlab library. Install with: pip install reportlab"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF generation failed: {str(e)}"
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Use 'json', 'csv', or 'pdf'."
        )


@router.get("/{experiment_id}/iterations/{iteration_id}", dependencies=[Depends(verify_api_key)])
async def get_iteration_details(
    experiment_id: UUID,
    iteration_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get detailed information for a specific iteration.
    """
    # Verify experiment exists
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get iteration
    iteration_repo = AttackIterationRepository(session)
    from sqlalchemy import select
    from core.database import AttackIterationDB
    
    stmt = select(AttackIterationDB).where(
        AttackIterationDB.iteration_id == iteration_id,
        AttackIterationDB.experiment_id == experiment_id
    )
    result = await session.execute(stmt)
    iteration = result.scalar_one_or_none()
    
    if not iteration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Iteration {iteration_id} not found for experiment {experiment_id}"
        )
    
    return api_response({
        "iteration_id": str(iteration.iteration_id),
        "experiment_id": str(experiment_id),
        "iteration_number": iteration.iteration_number,
        "strategy_used": iteration.strategy_used,
        "original_prompt": iteration.original_prompt,
        "mutated_prompt": iteration.mutated_prompt,
        "target_response": iteration.target_response,
        "judge_score": iteration.judge_score,
        "judge_reasoning": iteration.judge_reasoning,
        "success": iteration.success,
        "latency_ms": iteration.latency_ms,
        "timestamp": iteration.timestamp.isoformat() if iteration.timestamp else None,
        "attacker_feedback": iteration.attacker_feedback
    })

