#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def create_korean_html_template(content, title="Report"):
    """
    한국어 폰트가 제대로 표시되는 HTML 템플릿 생성
    Chrome PDF 생성 시 한국어 폰트 문제 해결
    """
    
    html_template = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- Google Fonts - Noto Sans KR (한국어 최적화) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;300;400;500;700;900&display=swap" rel="stylesheet">
    
    <style>
        /* 전체 폰트 설정 - 한국어 우선 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', 'Nanum Gothic', 'Dotum', sans-serif;
            font-size: 12px;
            line-height: 1.6;
            color: #333333;
            background: white;
            padding: 20px;
            font-weight: 400;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* 제목 폰트 설정 */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
            font-weight: 700;
            margin-bottom: 12px;
            margin-top: 20px;
            color: #2c3e50;
            word-break: keep-all;
            line-height: 1.4;
        }}
        
        h1 {{ 
            font-size: 24px; 
            font-weight: 900;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        h2 {{ 
            font-size: 20px; 
            font-weight: 700;
            color: #34495e;
        }}
        
        h3 {{ 
            font-size: 16px; 
            font-weight: 600;
            color: #7f8c8d;
        }}
        
        /* 본문 텍스트 */
        p {{
            margin-bottom: 12px;
            font-weight: 400;
            word-break: keep-all;
            line-height: 1.7;
        }}
        
        /* 리스트 스타일 */
        ul, ol {{
            margin-left: 20px;
            margin-bottom: 12px;
        }}
        
        li {{
            margin-bottom: 6px;
            line-height: 1.6;
        }}
        
        /* 테이블 스타일 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-family: 'Noto Sans KR', sans-serif;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            font-size: 11px;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        
        /* 강조 텍스트 */
        strong, b {{
            font-weight: 700;
        }}
        
        em, i {{
            font-style: italic;
        }}
        
        /* 페이지 나누기 */
        .page-break {{
            page-break-before: always;
        }}
        
        /* 인쇄용 스타일 */
        @media print {{
            body {{
                font-size: 11px;
                padding: 15px;
            }}
            
            h1 {{ font-size: 20px; }}
            h2 {{ font-size: 16px; }}
            h3 {{ font-size: 14px; }}
        }}
        
        /* Chrome PDF 생성 시 폰트 렌더링 최적화 */
        @page {{
            margin: 1cm;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>'''
    
    return html_template

def fix_existing_pdf():
    """
    기존 PDF를 다시 생성하여 한국어 폰트 문제 해결
    """
    import subprocess
    import os
    
    # 샘플 한국어 콘텐츠
    sample_content = """
    <h1>노트북 성능 비교 보고서</h1>
    
    <h2>1. 개요</h2>
    <p>최근 2년간 출시된 노트북 모델들의 성능을 종합적으로 비교 분석한 결과를 제시합니다.</p>
    
    <h2>2. 주요 브랜드별 분석</h2>
    
    <h3>2.1 ASUS 브랜드</h3>
    <p>ASUS는 다양한 가격대의 모델을 제공하며, 특히 젠북(Zenbook) 시리즈가 주목받고 있습니다.</p>
    <ul>
        <li>평균 가격: 2,247,500원</li>
        <li>배터리 수명: 평균 10.5시간</li>
        <li>주요 특징: OLED 디스플레이 옵션 제공</li>
    </ul>
    
    <h3>2.2 Apple MacBook</h3>
    <p>M3 칩셋을 탑재한 맥북 시리즈는 뛰어난 성능과 배터리 효율성을 보여줍니다.</p>
    <ul>
        <li>평균 가격: 1,890,000원</li>
        <li>배터리 수명: 평균 15.0시간</li>
        <li>주요 특징: 통합 메모리 구조와 최적화된 성능</li>
    </ul>
    
    <h2>3. 성능 비교 결과</h2>
    
    <table>
        <tr>
            <th>모델명</th>
            <th>브랜드</th>
            <th>가격</th>
            <th>종합점수</th>
        </tr>
        <tr>
            <td>MacBook Air M3</td>
            <td>Apple</td>
            <td>1,590,000원</td>
            <td>78.3점</td>
        </tr>
        <tr>
            <td>MacBook Pro M3</td>
            <td>Apple</td>
            <td>2,190,000원</td>
            <td>77.5점</td>
        </tr>
        <tr>
            <td>Zenbook S14</td>
            <td>ASUS</td>
            <td>2,500,000원</td>
            <td>68.9점</td>
        </tr>
    </table>
    
    <h2>4. 결론 및 추천</h2>
    <p><strong>가성비를 고려할 때 MacBook Air M3가 가장 우수한 선택지로 평가됩니다.</strong></p>
    
    <p>개발 및 사무용으로 사용할 경우, 다음과 같이 추천합니다:</p>
    <ol>
        <li><strong>최고 추천:</strong> MacBook Air M3 (종합점수 78.3점)</li>
        <li><strong>고성능 필요시:</strong> MacBook Pro M3 (종합점수 77.5점)</li>
        <li><strong>Windows 환경 선호시:</strong> ASUS Zenbook S14 (종합점수 68.9점)</li>
    </ol>
    """
    
    # 한국어 폰트가 적용된 HTML 생성
    html_content = create_korean_html_template(sample_content, "노트북 성능 비교 보고서")
    
    # HTML 파일 저장
    html_file = "fixed_korean_report.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 한국어 폰트가 적용된 HTML 파일 생성: {html_file}")
    
    # Chrome으로 PDF 생성 (한국어 폰트 지원 강화)
    pdf_file = "fixed_korean_report.pdf"
    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless",
        "--disable-gpu",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--run-all-compositor-stages-before-draw",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        f"--print-to-pdf={pdf_file}",
        "--print-to-pdf-no-header",
        "--virtual-time-budget=5000",
        "--font-render-hinting=none",
        html_file
    ]
    
    try:
        result = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 한국어 폰트가 적용된 PDF 생성 성공: {pdf_file}")
            print(f"📄 {result.stderr}")
            
            # 파일 크기 확인
            if os.path.exists(pdf_file):
                size = os.path.getsize(pdf_file)
                print(f"📊 생성된 PDF 크기: {size:,} bytes")
        else:
            print(f"❌ PDF 생성 실패: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ PDF 생성 시간 초과")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        # 임시 HTML 파일은 유지 (확인용)
        print(f"🔍 HTML 파일 확인: {html_file}")

if __name__ == "__main__":
    fix_existing_pdf()
