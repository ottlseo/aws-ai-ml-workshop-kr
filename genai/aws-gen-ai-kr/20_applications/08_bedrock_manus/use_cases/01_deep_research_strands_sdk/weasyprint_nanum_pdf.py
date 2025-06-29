#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def create_nanum_gothic_html_template(content, title="Report"):
    """
    나눔고딕 폰트를 사용하는 HTML 템플릿 생성 (WeasyPrint용)
    """
    
    html_template = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    
    <style>
        /* 나눔고딕 폰트 설정 */
        @font-face {{
            font-family: 'NanumGothic';
            src: local('Nanum Gothic'), local('NanumGothic');
            font-weight: normal;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'NanumGothic';
            src: local('Nanum Gothic Bold'), local('NanumGothic-Bold');
            font-weight: bold;
            font-style: normal;
        }}
        
        /* 전체 스타일 설정 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'NanumGothic', 'Nanum Gothic', 'Apple SD Gothic Neo', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333333;
            background: white;
            padding: 15mm;
            font-weight: normal;
        }}
        
        /* 제목 스타일 */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'NanumGothic', 'Nanum Gothic', sans-serif;
            font-weight: bold;
            margin-bottom: 8pt;
            margin-top: 16pt;
            color: #2c3e50;
            word-break: keep-all;
            line-height: 1.3;
        }}
        
        h1 {{ 
            font-size: 18pt; 
            border-bottom: 2pt solid #3498db;
            padding-bottom: 6pt;
            margin-bottom: 12pt;
        }}
        
        h2 {{ 
            font-size: 14pt; 
            color: #34495e;
            margin-top: 20pt;
        }}
        
        h3 {{ 
            font-size: 12pt; 
            color: #7f8c8d;
            margin-top: 16pt;
        }}
        
        /* 본문 텍스트 */
        p {{
            margin-bottom: 8pt;
            word-break: keep-all;
            line-height: 1.7;
            text-align: justify;
        }}
        
        /* 강조 텍스트 */
        strong, b {{
            font-weight: bold;
        }}
        
        em, i {{
            font-style: italic;
        }}
        
        /* 리스트 스타일 */
        ul, ol {{
            margin-left: 15pt;
            margin-bottom: 8pt;
        }}
        
        li {{
            margin-bottom: 4pt;
            line-height: 1.6;
        }}
        
        /* 테이블 스타일 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 12pt;
            font-size: 10pt;
        }}
        
        th, td {{
            border: 1pt solid #ddd;
            padding: 6pt;
            text-align: left;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        
        /* 페이지 나누기 */
        .page-break {{
            page-break-before: always;
        }}
        
        /* 인쇄용 페이지 설정 */
        @page {{
            size: A4;
            margin: 20mm;
        }}
        
        /* 구분선 */
        hr {{
            border: none;
            border-top: 1pt solid #ddd;
            margin: 16pt 0;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>'''
    
    return html_template

def generate_pdf_with_weasyprint(html_content, output_path):
    """
    WeasyPrint를 사용하여 HTML을 PDF로 변환
    """
    try:
        # 환경 변수 설정
        os.environ['DYLD_LIBRARY_PATH'] = "/opt/homebrew/lib:" + os.environ.get('DYLD_LIBRARY_PATH', '')
        os.environ['PKG_CONFIG_PATH'] = "/opt/homebrew/lib/pkgconfig:" + os.environ.get('PKG_CONFIG_PATH', '')
        
        # 폰트 설정
        font_config = FontConfiguration()
        
        # HTML을 PDF로 변환
        html_doc = HTML(string=html_content)
        pdf_bytes = html_doc.write_pdf(font_config=font_config)
        
        # PDF 파일 저장
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return True, f"PDF 생성 성공: {output_path}"
        
    except Exception as e:
        return False, f"PDF 생성 실패: {str(e)}"

def regenerate_laptop_report_with_weasyprint():
    """
    WeasyPrint와 나눔고딕을 사용하여 노트북 보고서 재생성
    """
    
    # 보고서 내용
    report_content = """
    <h1>최근 노트북 성능 비교 분석 보고서</h1>
    <p><em>2023-2025년 출시 모델 중심 분석</em></p>
    
    <div class="page-break"></div>
    
    <h2>1. 분석 개요</h2>
    <p>본 보고서는 최근 2년간 출시된 주요 노트북 모델들의 성능을 종합적으로 비교 분석한 결과입니다. 
    ASUS와 Apple MacBook 브랜드를 중심으로 가격, 성능, 배터리 수명 등을 다각도로 검토하였습니다.</p>
    
    <h2>2. 데이터 전처리 및 구조화 결과</h2>
    <p><strong>분석 기준일:</strong> 2025-06-30 00:19:06</p>
    
    <h3>2.1 브랜드별 가격대 분석</h3>
    <table>
        <tr>
            <th>브랜드</th>
            <th>평균 가격</th>
            <th>최소 가격</th>
            <th>최대 가격</th>
        </tr>
        <tr>
            <td>ASUS</td>
            <td>2,247,500원</td>
            <td>1,790,000원</td>
            <td>2,500,000원</td>
        </tr>
        <tr>
            <td>Mac</td>
            <td>1,890,000원</td>
            <td>1,590,000원</td>
            <td>2,190,000원</td>
        </tr>
    </table>
    
    <h3>2.2 배터리 수명 분석</h3>
    <ul>
        <li><strong>ASUS:</strong> 평균 10.5시간</li>
        <li><strong>Mac:</strong> 평균 15.0시간</li>
    </ul>
    
    <h3>2.3 주요 특징</h3>
    <ul>
        <li>ASUS는 다양한 화면 크기와 OLED 옵션 제공</li>
        <li>Mac은 통합 메모리 구조와 최적화된 배터리 성능 제공</li>
        <li>모든 모델이 개발 및 사무용으로 충분한 사양 보유</li>
    </ul>
    """
    
    # 나눔고딕 HTML 템플릿 생성
    html_content = create_nanum_gothic_html_template(report_content, "노트북 성능 비교 분석 보고서")
    
    # HTML 파일 저장
    html_file = "artifacts/weasyprint_nanum_report.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 나눔고딕 HTML 파일 생성: {html_file}")
    
    # WeasyPrint로 PDF 생성
    pdf_file = "artifacts/weasyprint_nanum_laptop_report.pdf"
    success, message = generate_pdf_with_weasyprint(html_content, pdf_file)
    
    if success:
        print(f"✅ {message}")
        
        # 파일 크기 확인
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file)
            print(f"📊 생성된 PDF 크기: {size:,} bytes")
            
            # 기존 파일들과 크기 비교
            original_size = os.path.getsize("artifacts/recent_laptops_performance_comparison_report.pdf")
            chrome_size = os.path.getsize("artifacts/fixed_recent_laptops_performance_comparison_report.pdf")
            
            print(f"📊 원본 PDF (문제 있음): {original_size:,} bytes")
            print(f"📊 Chrome PDF (수정됨): {chrome_size:,} bytes") 
            print(f"📊 WeasyPrint PDF (나눔고딕): {size:,} bytes")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    regenerate_laptop_report_with_weasyprint()
