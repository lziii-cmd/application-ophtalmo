"""
Génération de PDF pour les prescriptions médicales avec ReportLab.
"""

from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


def make_qr_image(data_str):
    """Génère un QR code en mémoire et retourne un ImageReader ReportLab."""
    try:
        import qrcode
        import io
        from reportlab.lib.utils import ImageReader
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(data_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return ImageReader(buf)
    except ImportError:
        return None


def get_styles():
    """Retourne les styles personnalisés pour les PDF médicaux."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ClinicHeader',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=2,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name='ClinicSubHeader',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#6c757d'),
        spaceAfter=2,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0d6efd'),
        spaceBefore=8,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name='FieldLabel',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#495057'),
        spaceAfter=1,
    ))

    styles.add(ParagraphStyle(
        name='FieldValue',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#212529'),
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name='SmallText',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica',
        textColor=colors.HexColor('#6c757d'),
    ))

    styles.add(ParagraphStyle(
        name='PrescriptionTitle',
        parent=styles['Normal'],
        fontSize=13,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#212529'),
        spaceBefore=10,
        spaceAfter=6,
        alignment=TA_CENTER,
    ))

    return styles


def build_header(story, medecin, styles):
    """Construit l'en-tête du document avec les informations du médecin."""
    medecin_name = medecin.get_full_name() or medecin.username
    specialite = getattr(medecin, 'specialite', '') or 'Ophtalmologiste'
    rpps = getattr(medecin, 'rpps', '') or ''
    telephone = getattr(medecin, 'telephone', '') or ''
    email = getattr(medecin, 'email', '') or ''

    style_right = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=10)
    style_right_sm = ParagraphStyle('RightSm', parent=styles['Normal'], alignment=TA_RIGHT,
                                    fontSize=9, textColor=colors.HexColor('#6c757d'))

    left_col = [
        Paragraph(f"Dr {medecin_name}", styles['ClinicHeader']),
        Paragraph(specialite, styles['ClinicSubHeader']),
    ]
    if rpps:
        left_col.append(Paragraph(f"RPPS : {rpps}", styles['ClinicSubHeader']))
    if telephone:
        left_col.append(Paragraph(f"Tel : {telephone}", styles['ClinicSubHeader']))

    right_col = [
        Paragraph("<b>Cabinet d'Ophtalmologie</b>", style_right),
        Paragraph("Dakar, Senegal", style_right_sm),
        Paragraph(f"Tel : {telephone}", style_right_sm) if telephone else Paragraph('', styles['Normal']),
        Paragraph(f"{email}", style_right_sm) if email else Paragraph('', styles['Normal']),
    ]

    # Construire en tableau 2 colonnes
    rows = []
    max_rows = max(len(left_col), len(right_col))
    for i in range(max_rows):
        l = left_col[i] if i < len(left_col) else Paragraph('', styles['Normal'])
        r = right_col[i] if i < len(right_col) else Paragraph('', styles['Normal'])
        rows.append([l, r])

    header_table = Table(rows, colWidths=[10*cm, 9*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#0d6efd'), spaceAfter=6))


def build_patient_info(story, patient, styles):
    """Construit le bloc informations patient."""
    story.append(Paragraph("PATIENT", styles['SectionTitle']))

    patient_data = [
        ['Nom et prénom:', patient.nom_complet, 'Date de naissance:', patient.date_naissance.strftime('%d/%m/%Y')],
        ['Âge:', f"{patient.age} ans", 'Téléphone:', patient.telephone],
    ]

    patient_table = Table(patient_data, colWidths=[4*cm, 7*cm, 4*cm, 4*cm])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#495057')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#495057')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 6))


def generate_prescription_pdf(prescription):
    """
    Génère un PDF pour une prescription médicale.
    Retourne un HttpResponse avec le contenu PDF.
    """
    buffer = BytesIO()

    medecin = prescription.medecin
    patient = prescription.consultation.patient

    # Préparer les données QR
    qr_data = (
        f"PRESC-{prescription.pk:06d}\n"
        f"Patient: {patient.nom_complet}\n"
        f"Médecin: Dr {medecin.get_full_name()}\n"
        f"Date: {prescription.date_creation.strftime('%d/%m/%Y')}\n"
        f"Type: {prescription.get_type_prescription_display()}"
    )
    qr_img = make_qr_image(qr_data)

    def on_first_page(canvas, doc):
        """Dessine le QR code en haut à droite sur la première page."""
        if qr_img:
            page_width, page_height = A4
            qr_size = 2.5 * cm
            x = page_width - doc.rightMargin - qr_size
            y = page_height - doc.topMargin - qr_size
            canvas.drawImage(qr_img, x, y, width=qr_size, height=qr_size, preserveAspectRatio=True)

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=f"Prescription - {patient.nom_complet}"
    )

    styles = get_styles()
    story = []

    # En-tête
    build_header(story, medecin, styles)

    # Informations patient
    build_patient_info(story, patient, styles)

    # Titre prescription
    type_labels = {
        'lunettes': 'ORDONNANCE LUNETTES',
        'traitement': 'PRESCRIPTION MÉDICALE',
        'examen': 'PRESCRIPTION D\'EXAMENS COMPLÉMENTAIRES',
        'lentilles': 'ORDONNANCE LENTILLES DE CONTACT',
    }
    story.append(Paragraph(
        type_labels.get(prescription.type_prescription, 'PRESCRIPTION'),
        styles['PrescriptionTitle']
    ))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#dee2e6'), spaceAfter=8))

    contenu = prescription.contenu

    if prescription.type_prescription == 'lunettes':
        _build_lunettes_content(story, contenu, styles)
    elif prescription.type_prescription == 'traitement':
        _build_traitement_content(story, contenu, styles)
    elif prescription.type_prescription == 'examen':
        _build_examen_content(story, contenu, styles)
    elif prescription.type_prescription == 'lentilles':
        _build_lentilles_content(story, contenu, styles)

    # Remarques
    remarques = contenu.get('remarques', '').strip()
    if remarques:
        story.append(Paragraph("Remarques:", styles['FieldLabel']))
        story.append(Paragraph(remarques, styles['FieldValue']))

    # Espace avant signature
    story.append(Spacer(1, 2*cm))

    # Signature
    sig_data = [
        ['', f"Le {timezone.now().strftime('%d/%m/%Y')}"],
        ['', f"Dr {medecin.get_full_name()}"],
        ['', ''],
        ['', 'Signature et cachet:'],
        ['', ''],
        ['', '_' * 30],
    ]
    sig_table = Table(sig_data, colWidths=[12*cm, 7*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    story.append(sig_table)

    # Pied de page
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#dee2e6')))

    medecin_tel = getattr(medecin, 'telephone', '') or ''
    medecin_email = getattr(medecin, 'email', '') or ''
    medecin_rpps = getattr(medecin, 'rpps', '') or ''

    footer_lines = []
    if medecin_tel or medecin_email:
        contact = '  •  '.join(filter(None, [medecin_tel, medecin_email]))
        footer_lines.append(contact)
    footer_lines.append(f"Ref : PRESC-{prescription.pk:06d}  —  emis le {prescription.date_creation.strftime('%d/%m/%Y')}")
    if medecin_rpps:
        footer_lines.append(f"RPPS : {medecin_rpps}")

    for line in footer_lines:
        story.append(Paragraph(line, styles['SmallText']))

    doc.build(story, onFirstPage=on_first_page)
    buffer.seek(0)

    # Marquer comme imprimée
    if not prescription.imprimee:
        prescription.imprimee = True
        prescription.save(update_fields=['imprimee'])

    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="prescription_{prescription.pk}_{prescription.consultation.patient.nom}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    )
    return response


def _build_lunettes_content(story, contenu, styles):
    """Contenu pour ordonnance lunettes."""
    story.append(Paragraph("Correction optique prescrite :", styles['SectionTitle']))

    od = contenu.get('oeil_droit', {})
    og = contenu.get('oeil_gauche', {})

    data = [
        ['Oeil', 'Sphere', 'Cylindre', 'Axe', 'Addition'],
        [
            'Oeil droit (OD)',
            od.get('sphere', '-') or '-',
            od.get('cylindre', '-') or '-',
            od.get('axe', '-') or '-',
            od.get('addition', '-') or '-',
        ],
        [
            'Oeil gauche (OG)',
            og.get('sphere', '-') or '-',
            og.get('cylindre', '-') or '-',
            og.get('axe', '-') or '-',
            og.get('addition', '-') or '-',
        ],
    ]

    table = Table(data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    story.append(Spacer(1, 6))


def _build_traitement_content(story, contenu, styles):
    """Contenu pour prescription médicale."""
    medicaments = contenu.get('medicaments', [])
    if not medicaments:
        story.append(Paragraph("Aucun médicament prescrit.", styles['FieldValue']))
        return

    for i, med in enumerate(medicaments, 1):
        story.append(Paragraph(f"{i}. {med.get('nom', 'Médicament sans nom')}", styles['SectionTitle']))
        details = []
        if med.get('posologie'):
            details.append(f"<b>Posologie:</b> {med['posologie']}")
        if med.get('duree'):
            details.append(f"<b>Durée:</b> {med['duree']}")
        if med.get('instructions'):
            details.append(f"<b>Instructions:</b> {med['instructions']}")
        if details:
            story.append(Paragraph('  |  '.join(details), styles['FieldValue']))
        story.append(Spacer(1, 4))


def _build_examen_content(story, contenu, styles):
    """Contenu pour prescription d'examens."""
    examens = contenu.get('examens', [])
    if not examens:
        story.append(Paragraph("Aucun examen prescrit.", styles['FieldValue']))
        return

    urgence_labels = {
        '': 'Normal',
        'urgent': 'URGENT',
        'tres_urgent': 'TRÈS URGENT',
    }
    urgence_colors = {
        '': colors.HexColor('#198754'),
        'urgent': colors.HexColor('#fd7e14'),
        'tres_urgent': colors.HexColor('#dc3545'),
    }

    for i, examen in enumerate(examens, 1):
        nom = examen.get('nom', 'Examen sans nom')
        indication = examen.get('indication', '')
        urgence = examen.get('urgence', '')

        urgence_label = urgence_labels.get(urgence, 'Normal')
        story.append(Paragraph(f"{i}. {nom} — <font color='#{urgence_colors.get(urgence, colors.green).hexval()[2:]}'>{urgence_label}</font>", styles['SectionTitle']))
        if indication:
            story.append(Paragraph(f"Indication: {indication}", styles['FieldValue']))
        story.append(Spacer(1, 4))


def _build_lentilles_content(story, contenu, styles):
    """Contenu pour ordonnance lentilles."""
    story.append(Paragraph("Prescription de lentilles de contact :", styles['SectionTitle']))

    od = contenu.get('oeil_droit', {})
    og = contenu.get('oeil_gauche', {})

    data = [
        ['Oeil', 'Rayon', 'Diametre', 'Puissance', 'Marque'],
        [
            'Oeil droit (OD)',
            od.get('rayon', '-') or '-',
            od.get('diametre', '-') or '-',
            od.get('puissance', '-') or '-',
            od.get('marque', '-') or '-',
        ],
        [
            'Oeil gauche (OG)',
            og.get('rayon', '-') or '-',
            og.get('diametre', '-') or '-',
            og.get('puissance', '-') or '-',
            og.get('marque', '-') or '-',
        ],
    ]

    table = Table(data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    renouvellement = contenu.get('renouvellement', '')
    if renouvellement:
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Renouvellement: {renouvellement}", styles['FieldValue']))
    story.append(Spacer(1, 6))


def generate_patient_record_pdf(patient):
    """
    Génère le dossier complet d'un patient en PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=f"Dossier patient - {patient.nom_complet}"
    )

    styles = get_styles()
    story = []

    # Titre
    story.append(Paragraph("DOSSIER MÉDICAL PATIENT", styles['PrescriptionTitle']))
    story.append(Paragraph(
        f"Généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}",
        styles['ClinicSubHeader']
    ))
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#0d6efd'), spaceAfter=10))

    # Informations patient
    story.append(Paragraph("IDENTITÉ DU PATIENT", styles['SectionTitle']))
    patient_data = [
        ['Nom:', patient.nom, 'Prénom:', patient.prenom],
        ['Date de naissance:', patient.date_naissance.strftime('%d/%m/%Y'), 'Âge:', f"{patient.age} ans"],
        ['Sexe:', patient.get_sexe_display(), 'Téléphone:', patient.telephone],
        ['Email:', patient.email or '-', 'Adresse:', patient.adresse or '-'],
        ['Statut:', patient.get_statut_display(), 'Dossier N°:', str(patient.pk).zfill(6)],
    ]

    pt = Table(patient_data, colWidths=[4*cm, 6*cm, 4*cm, 5*cm])
    pt.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(pt)

    # Antécédents et allergies
    if patient.antecedents or patient.allergies or patient.traitements_en_cours:
        story.append(Paragraph("INFORMATIONS MÉDICALES", styles['SectionTitle']))
        if patient.allergies:
            story.append(Paragraph("Allergies:", styles['FieldLabel']))
            story.append(Paragraph(patient.allergies, styles['FieldValue']))
        if patient.antecedents:
            story.append(Paragraph("Antécédents:", styles['FieldLabel']))
            story.append(Paragraph(patient.antecedents, styles['FieldValue']))
        if patient.traitements_en_cours:
            story.append(Paragraph("Traitements en cours:", styles['FieldLabel']))
            story.append(Paragraph(patient.traitements_en_cours, styles['FieldValue']))

    # Consultations
    consultations = patient.consultations.filter(
        statut__in=['valide', 'brouillon']
    ).order_by('-date_heure')[:10]

    if consultations:
        story.append(Paragraph("HISTORIQUE DES CONSULTATIONS", styles['SectionTitle']))
        for c in consultations:
            consult_data = [
                [f"Consultation du {c.date_heure.strftime('%d/%m/%Y')} — Dr {c.medecin.get_full_name()} — {c.get_statut_display()}", ''],
                ['Diagnostic:', c.diagnostic_principal or '-'],
            ]
            if c.tension_od or c.tension_og:
                consult_data.append(['Tensions OD/OG:', f"{c.tension_od or '-'} / {c.tension_og or '-'} mmHg"])
            if c.acuite_od_loin or c.acuite_og_loin:
                consult_data.append(['Acuité OD/OG:', f"{c.acuite_od_loin or '-'} / {c.acuite_og_loin or '-'}"])

            ct = Table(consult_data, colWidths=[4*cm, 14*cm])
            ct.setStyle(TableStyle([
                ('SPAN', (0, 0), (-1, 0)),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7f1ff')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
            ]))
            story.append(ct)
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="dossier_patient_{patient.pk}_{patient.nom}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    )
    return response
