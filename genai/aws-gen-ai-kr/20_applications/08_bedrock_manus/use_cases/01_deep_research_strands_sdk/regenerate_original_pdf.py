#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
from fix_korean_font_html import create_korean_html_template

def regenerate_laptop_report_pdf():
    """
    원본 노트북 보고서를 한국어 폰트가 적용된 PDF로 재생성
    """
    
    # 원본 보고서 내용 (artifacts/all_results.txt 기반)
    report_content = """
    <h1>최근 노트북 성능 비교 분석 보고서</h1>
    <p><em>2023-2025년 출시 모델 중심</em></p>
    
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
    
    <div class="page-break"></div>
    
    <h2>3. 가격 대비 성능 분석</h2>
    
    <h3>3.1 성능 점수 분석</h3>
    <ul>
        <li><strong>최고 성능 모델:</strong> MacBook Pro M3 (점수: 51.7)</li>
        <li><strong>최저 성능 모델:</strong> 2024 비보북 프로 15 OLED (점수: 40.4)</li>
    </ul>
    
    <h3>3.2 가성비 분석</h3>
    <ul>
        <li><strong>최고 가성비 모델:</strong> MacBook Air M3 (가성비 점수: 30.00)</li>
        <li><strong>최저 가성비 모델:</strong> Zenbook S16 (가성비 점수: 18.64)</li>
    </ul>
    
    <h3>3.3 분석 방법론</h3>
    <ul>
        <li>성능 점수 계산: RAM(30%), 배터리(30%), 프로세서(40%) 가중치 적용</li>
        <li>가성비 점수: (성능 점수 × 1,000,000) ÷ 가격</li>
    </ul>
    
    <div class="page-break"></div>
    
    <h2>4. 배터리 성능 상세 분석</h2>
    
    <h3>4.1 브랜드별 배터리 성능</h3>
    <table>
        <tr>
            <th>브랜드</th>
            <th>평균 수명</th>
            <th>최소 수명</th>
            <th>최대 수명</th>
            <th>표준편차</th>
        </tr>
        <tr>
            <td>ASUS</td>
            <td>10.5시간</td>
            <td>10.0시간</td>
            <td>12.0시간</td>
            <td>1.00</td>
        </tr>
        <tr>
            <td>Mac</td>
            <td>15.0시간</td>
            <td>15.0시간</td>
            <td>15.0시간</td>
            <td>0.00</td>
        </tr>
    </table>
    
    <h3>4.2 사용 시나리오별 배터리 수명</h3>
    <ul>
        <li><strong>일반 사무작업:</strong> 모든 모델이 8시간 이상 업무 가능</li>
        <li><strong>개발 작업:</strong> Mac 10시간 이상, ASUS 7-8시간</li>
        <li><strong>고성능 작업:</strong> 모든 모델 3-4시간으로 감소</li>
    </ul>
    
    <div class="page-break"></div>
    
    <h2>5. 프로세서 성능 및 다중작업 능력</h2>
    
    <h3>5.1 성능 비교</h3>
    <table>
        <tr>
            <th>성능 지표</th>
            <th>ASUS 평균</th>
            <th>Mac 평균</th>
        </tr>
        <tr>
            <td>싱글코어 성능</td>
            <td>88.8점 (85.0~90.0)</td>
            <td>97.5점 (95.0~100.0)</td>
        </tr>
        <tr>
            <td>멀티코어 성능</td>
            <td>83.8점 (80.0~85.0)</td>
            <td>95.0점 (90.0~100.0)</td>
        </tr>
        <tr>
            <td>전력 효율성</td>
            <td>83.8점</td>
            <td>95.0점</td>
        </tr>
    </table>
    
    <h3>5.2 개발 작업 시 성능 특징</h3>
    <ul>
        <li><strong>Mac M3 시리즈:</strong>
            <ul>
                <li>싱글코어, 멀티코어 모두 우수한 성능</li>
                <li>전력 효율성이 매우 뛰어남</li>
                <li>개발 도구 최적화가 잘 되어있음</li>
            </ul>
        </li>
        <li><strong>ASUS Intel 시리즈:</strong>
            <ul>
                <li>안정적인 성능 제공</li>
                <li>다양한 개발 환경과의 호환성 우수</li>
                <li>멀티태스킹 시 발열 관리 중요</li>
            </ul>
        </li>
    </ul>
    
    <div class="page-break"></div>
    
    <h2>6. 종합 점수 및 최종 추천</h2>
    
    <h3>6.1 종합 점수 산출 방식</h3>
    <ul>
        <li>성능 점수 (40%): 프로세서 성능 기준</li>
        <li>RAM 점수 (20%): 메모리 용량 기준</li>
        <li>배터리 점수 (20%): 배터리 수명 기준</li>
        <li>가격 점수 (20%): 가격 대비 역산 점수</li>
    </ul>
    
    <h3>6.2 종합 점수 순위</h3>
    <table>
        <tr>
            <th>순위</th>
            <th>모델명</th>
            <th>종합 점수</th>
            <th>브랜드</th>
        </tr>
        <tr>
            <td>1위</td>
            <td>MacBook Air M3</td>
            <td>78.3점</td>
            <td>Mac</td>
        </tr>
        <tr>
            <td>2위</td>
            <td>MacBook Pro M3</td>
            <td>77.5점</td>
            <td>Mac</td>
        </tr>
        <tr>
            <td>3위</td>
            <td>Zenbook S14</td>
            <td>68.9점</td>
            <td>ASUS</td>
        </tr>
        <tr>
            <td>4위</td>
            <td>Zenbook S 16 OLED</td>
            <td>68.1점</td>
            <td>ASUS</td>
        </tr>
        <tr>
            <td>5위</td>
            <td>Zenbook S16</td>
            <td>67.3점</td>
            <td>ASUS</td>
        </tr>
        <tr>
            <td>6위</td>
            <td>2024 비보북 프로 15 OLED</td>
            <td>63.7점</td>
            <td>ASUS</td>
        </tr>
    </table>
    
    <div class="page-break"></div>
    
    <h2>7. 최종 결론 및 구매 가이드</h2>
    
    <h3>7.1 사용 목적별 최적 모델</h3>
    
    <h4>개발/프로그래밍용</h4>
    <ol>
        <li><strong>1순위: MacBook Air M3</strong> (종합 점수: 78.3점)
            <ul>
                <li>뛰어난 가성비와 배터리 성능</li>
                <li>개발 도구 최적화</li>
                <li>가격: 1,590,000원</li>
            </ul>
        </li>
        <li><strong>2순위: MacBook Pro M3</strong> (종합 점수: 77.5점)
            <ul>
                <li>최고 성능이 필요한 경우</li>
                <li>가격: 2,190,000원</li>
            </ul>
        </li>
    </ol>
    
    <h4>일반 사무용</h4>
    <ol>
        <li><strong>1순위: Zenbook S14</strong> (종합 점수: 68.9점)
            <ul>
                <li>Windows 환경 선호 시</li>
                <li>다양한 소프트웨어 호환성</li>
                <li>가격: 2,500,000원</li>
            </ul>
        </li>
        <li><strong>2순위: Zenbook S 16 OLED</strong> (종합 점수: 68.1점)
            <ul>
                <li>대화면과 OLED 디스플레이</li>
                <li>멀티미디어 작업에 적합</li>
            </ul>
        </li>
    </ol>
    
    <h3>7.2 브랜드별 평균 종합 점수</h3>
    <ul>
        <li><strong>Mac:</strong> 77.9점 (일관된 고성능)</li>
        <li><strong>ASUS:</strong> 67.0점 (다양한 선택지)</li>
    </ul>
    
    <h3>7.3 최종 권장사항</h3>
    <p><strong>전체적으로 MacBook Air M3가 가격, 성능, 배터리 수명을 종합했을 때 가장 균형잡힌 선택</strong>으로 평가됩니다. 
    Windows 환경이 필요하거나 더 큰 화면을 원하는 경우에는 ASUS Zenbook 시리즈를 고려할 수 있습니다.</p>
    
    <hr style="margin: 20px 0;">
    <p><em>본 보고서는 2025년 6월 기준으로 작성되었으며, 실제 구매 시에는 최신 가격과 사양을 확인하시기 바랍니다.</em></p>
    """
    
    # 한국어 폰트가 적용된 HTML 생성
    html_content = create_korean_html_template(report_content, "최근 노트북 성능 비교 분석 보고서")
    
    # HTML 파일 저장
    html_file = "artifacts/fixed_recent_laptops_report.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 수정된 HTML 파일 생성: {html_file}")
    
    # Chrome으로 PDF 생성 (한국어 폰트 지원)
    pdf_file = "artifacts/fixed_recent_laptops_performance_comparison_report.pdf"
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
            print(f"✅ 한국어 폰트가 적용된 원본 보고서 PDF 생성 성공!")
            print(f"📄 파일 위치: {pdf_file}")
            print(f"📊 {result.stderr}")
            
            # 파일 크기 비교
            if os.path.exists(pdf_file):
                new_size = os.path.getsize(pdf_file)
                old_size = os.path.getsize("artifacts/recent_laptops_performance_comparison_report.pdf")
                print(f"📊 기존 PDF 크기: {old_size:,} bytes")
                print(f"📊 새 PDF 크기: {new_size:,} bytes")
                print(f"📊 크기 차이: {new_size - old_size:+,} bytes")
        else:
            print(f"❌ PDF 생성 실패: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ PDF 생성 시간 초과")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    regenerate_laptop_report_pdf()
