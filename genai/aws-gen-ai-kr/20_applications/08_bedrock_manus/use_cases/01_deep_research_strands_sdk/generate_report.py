import json
import boto3
import base64
import os
import re
import ast
import traceback
from datetime import datetime
from botocore.exceptions import ClientError

def get_named_parameter(event, name):
    """
    이벤트에서 특정 이름의 파라미터 값을 추출합니다.
    
    Parameters:
    - event: Lambda 이벤트 객체
    - name: 파라미터 이름
    
    Returns:
    - 파라미터 값 또는 None (파라미터가 없는 경우)
    """
    print(f"파라미터 추출 시도: {name}, 이벤트 파라미터: {event.get('parameters', [])}")
    for param in event.get('parameters', []):
        if param['name'] == name:
            print(f"파라미터 {name} 값: {param['value'][:100] if isinstance(param['value'], str) and len(param['value']) > 100 else param['value']}")
            return param['value']
    print(f"파라미터 {name}을(를) 찾을 수 없음")
    return None

def generate_report(s3_uri, analyses, report_format='html', report_title='분석 보고서', report_language='ko'):
    """
    분석 결과를 기반으로 보고서를 생성하는 함수
    
    Parameters:
    - s3_uri: S3 URI (형식: s3://bucket-name/prefix)
    - analyses: 분석 결과 목록
    - report_format: 보고서 형식 ('html', 'pdf', 'markdown' 중 하나)
    - report_title: 보고서 제목
    - report_language: 보고서 언어 ('ko' 또는 'en')
    
    Returns:
    - 생성된 보고서 파일의 S3 URL을 포함하는 응답
    """
    print(f"generate_report 함수 시작: s3_uri={s3_uri}, format={report_format}, title={report_title}, language={report_language}")
    
    try:
        if not s3_uri:
            print("S3 URI가 제공되지 않았습니다.")
            return {
                'error': 'S3 URI가 제공되지 않았습니다.'
            }
            
        if not analyses:
            print("분석 결과가 제공되지 않았습니다.")
            return {
                'error': '분석 결과가 제공되지 않았습니다.'
            }
        
        # 분석 결과 검증
        valid_analyses = []
        for analysis in analyses:
            if not isinstance(analysis, dict):
                print(f"유효하지 않은 분석 결과 형식: {type(analysis)}")
                continue
                
            # 필수 필드만 검증 (name과 results만 필수로 변경)
            if 'name' not in analysis or 'results' not in analysis:
                print(f"필수 필드가 없는 분석 결과: {list(analysis.keys())}")
                continue
            
            # references 필드가 없으면 빈 배열로 초기화
            if 'references' not in analysis:
                analysis['references'] = []
                
            # artifacts 필드가 없으면 빈 배열로 초기화
            if 'artifacts' not in analysis:
                analysis['artifacts'] = []
                
            valid_analyses.append(analysis)
            
        if not valid_analyses:
            print("유효한 분석 결과가 없습니다.")
            return {
                'error': '유효한 분석 결과가 제공되지 않았습니다.'
            }
            
        analyses = valid_analyses
        print(f"유효한 분석 결과 수: {len(analyses)}")
        
        # S3 URI 파싱
        if s3_uri.startswith('s3://'):
            s3_uri = s3_uri[5:]  # 's3://' 제거
        
        parts = s3_uri.split('/', 1)
        bucket_name = parts[0]
        prefix = parts[1] if len(parts) > 1 else ''
        
        # S3 클라이언트 생성
        s3_client = boto3.client('s3')
        
        # 현재 시간을 파일 이름에 포함
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 보고서 생성
        print(f"보고서 생성 시작: {report_format}")
        if report_format == 'html':
            report_content, content_type = generate_html_report(analyses, report_title, report_language)
            file_extension = 'html'
        elif report_format == 'pdf':
            # HTML을 먼저 생성한 후 PDF로 변환
            print("HTML 생성 후 PDF로 변환")
            html_content, _ = generate_html_report(analyses, report_title, report_language)
            report_content = convert_html_to_pdf(html_content, report_language)
            content_type = 'application/pdf'
            file_extension = 'pdf'
        elif report_format == 'markdown':
            report_content, content_type = generate_markdown_report(analyses, report_title, report_language)
            file_extension = 'md'
        else:
            print(f"지원되지 않는 보고서 형식: {report_format}")
            return {
                'error': f"지원되지 않는 보고서 형식: {report_format}"
            }
        
        print(f"보고서 생성 완료: {len(report_content)} 바이트, 콘텐츠 타입: {content_type}")
        
        # 보고서 파일 이름 생성
        report_filename = f"report_{timestamp}.{file_extension}"
        report_key = f"{prefix.rstrip('/')}/reports/{report_filename}" if prefix else f"reports/{report_filename}"
        
        print(f"보고서 파일 업로드: {bucket_name}/{report_key}")
        
        # 보고서 파일을 S3에 업로드
        s3_client.put_object(
            Bucket=bucket_name,
            Key=report_key,
            Body=report_content,
            ContentType=content_type
        )
        
        # 보고서 파일에 대한 S3 URL 생성
        report_url = f"https://{bucket_name}.s3.amazonaws.com/{report_key}"
        print(f"보고서 URL: {report_url}")
        
        return {
            'report_url': report_url,
            'report_format': report_format,
            'message': '보고서가 성공적으로 생성되었습니다.'
        }
        
    except Exception as e:
        print(f"보고서 생성 중 오류 발생: {str(e)}")
        traceback.print_exc()
        return {
            'error': f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        }

def generate_html_report(analyses, report_title, language='ko'):
    """
    분석 결과를 기반으로 HTML 보고서를 생성합니다.
    
    Parameters:
    - analyses: 분석 결과 목록
    - report_title: 보고서 제목
    - language: 보고서 언어 ('ko' 또는 'en')
    
    Returns:
    - HTML 보고서 내용 및 콘텐츠 타입
    """
    print(f"generate_html_report 함수 시작: title={report_title}, language={language}")
    print(f"analyses 타입: {type(analyses)}, 길이: {len(analyses) if isinstance(analyses, list) else 'N/A'}")
    
    # 언어에 따른 텍스트 설정
    texts = {
        'ko': {
            'summary': '요약',
            'key_findings': '주요 발견사항',
            'detailed_analysis': '상세 분석',
            'conclusions': '결론 및 권장사항',
            'execution_time': '실행 시간',
            'no_artifacts': '생성된 아티팩트 없음',
            'generated_files': '생성된 파일'
        },
        'en': {
            'summary': 'Summary',
            'key_findings': 'Key Findings',
            'detailed_analysis': 'Detailed Analysis',
            'conclusions': 'Conclusions & Recommendations',
            'execution_time': 'Execution Time',
            'no_artifacts': 'No artifacts generated',
            'generated_files': 'Generated Files'
        }
    }
    
    # 기본 언어를 한국어로 설정
    t = texts.get(language, texts['ko'])
    print(f"언어 설정: {language}, 텍스트: {t}")
    
    # HTML 헤더 생성
    print("HTML 헤더 생성")
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report_title}</title>
    <style>
        body {{
            font-family: {'"Nanum Gothic", sans-serif' if language == 'ko' else '"Noto Sans", sans-serif'};
            margin: 2cm;
            line-height: 1.5;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #3498db;
            margin-top: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #2c3e50;
            margin-top: 15px;
        }}
        .content {{
            margin-top: 20px;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #ddd;
        }}
        .image-caption {{
            text-align: center;
            font-style: italic;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .artifact-list {{
            margin-left: 20px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>{report_title}</h1>
    
    <h2>{t['summary']}</h2>
    <div class="content">
        <p>이 보고서는 {len(analyses)}개의 분석 단계에서 생성된 결과를 종합한 것입니다.</p>
    </div>
    
    <h2>{t['key_findings']}</h2>
    <div class="content">
        <ul>
"""
    
    # 주요 발견사항 추가
    print("주요 발견사항 추가")
    for i, analysis in enumerate(analyses):
        try:
            print(f"분석 {i+1} 발견사항 추가: {analysis['name']}")
            html += f"            <li><strong>{analysis['name']}</strong>: {analysis['results']}</li>\n"
        except Exception as e:
            print(f"분석 {i+1} 발견사항 추가 중 오류: {str(e)}")
            print(f"분석 {i+1} 내용: {analysis}")
            traceback.print_exc()
    
    html += """        </ul>
    </div>
    
    <h2>{}</h2>
""".format(t['detailed_analysis'])
    
    # 각 분석 단계에 대한 상세 내용 추가
    print("상세 분석 내용 추가")
    for i, analysis in enumerate(analyses):
        try:
            print(f"분석 {i+1} 상세 내용 추가: {analysis['name']}")
            html += f"""    <div class="content">
        <h3>{analysis['name']}</h3>
        <p class="timestamp">{t['execution_time']}: {analysis['time']}</p>
"""
            
            # 결과 텍스트 처리 - 불렛 포인트와 줄바꿈 개선
            results_text = analysis['results']
            
            # 불렛 포인트(•) 처리
            if '•' in results_text:
                # 불렛 포인트로 분리
                sections = results_text.split('•')
                
                # 첫 번째 섹션은 일반 텍스트로 처리
                if sections[0].strip():
                    html += f"        <p>{sections[0].strip()}</p>\n\n"
                
                # 나머지 섹션은 불렛 포인트로 처리
                if len(sections) > 1:
                    html += "        <ul>\n"
                    for section in sections[1:]:
                        if not section.strip():
                            continue
                        
                        # 하위 불렛 포인트(-) 처리
                        if '-' in section:
                            main_point = section.split('-')[0].strip()
                            sub_points = section.split('-')[1:]
                            
                            html += f"            <li>{main_point}\n"
                            html += "                <ul>\n"
                            for sub_point in sub_points:
                                if sub_point.strip():
                                    html += f"                    <li>{sub_point.strip()}</li>\n"
                            html += "                </ul>\n"
                            html += "            </li>\n"
                        else:
                            html += f"            <li>{section.strip()}</li>\n"
                    html += "        </ul>\n\n"
            # 일반 텍스트 처리
            else:
                # 줄바꿈 처리
                paragraphs = results_text.split('\n\n')
                for paragraph in paragraphs:
                    if not paragraph.strip():
                        continue
                    
                    # 번호 목록 처리 (1. 2. 3. 등)
                    if re.search(r'^\d+\.', paragraph.strip()):
                        lines = paragraph.strip().split('\n')
                        html += "        <ol>\n"
                        for line in lines:
                            if re.search(r'^\d+\.', line.strip()):
                                item_text = re.sub(r'^\d+\.', '', line.strip()).strip()
                                html += f"            <li>{item_text}</li>\n"
                        html += "        </ol>\n\n"
                    else:
                        html += f"        <p>{paragraph.strip()}</p>\n\n"
            
            html += f"""        
        <h4>{t['generated_files']}</h4>
"""
            
            if not analysis['artifacts']:
                print(f"분석 {i+1}: 아티팩트 없음")
                html += f"        <p>{t['no_artifacts']}</p>\n"
            else:
                print(f"분석 {i+1}: {len(analysis['artifacts'])}개의 아티팩트 추가")
                html += "        <div class=\"artifact-list\">\n"
                
                for j, artifact in enumerate(analysis['artifacts']):
                    try:
                        print(f"분석 {i+1}, 아티팩트 {j+1} 추가: {artifact['path']}")
                        html += f"            <p><strong>{artifact['path']}</strong>: {artifact['description']}</p>\n"
                        
                        # 이미지 S3 URI가 있는 경우 이미지 추가
                        if 's3_uri' in artifact:
                            print(f"분석 {i+1}, 아티팩트 {j+1}: 이미지 S3 URI 추가")
                            s3_uri = artifact['s3_uri']
                            
                            # S3에서 이미지 파일 로드
                            try:
                                # S3 URI 파싱
                                if s3_uri.startswith('s3://'):
                                    s3_uri = s3_uri[5:]  # 's3://' 제거
                                
                                parts = s3_uri.split('/', 1)
                                img_bucket = parts[0]
                                img_key = parts[1] if len(parts) > 1 else ''
                                
                                # S3에서 이미지 파일 로드
                                try:
                                    print(f"S3에서 이미지 로드 시도: {img_bucket}/{img_key}")
                                    img_response = s3_client.get_object(Bucket=img_bucket, Key=img_key)
                                    image_data = img_response['Body'].read()
                                    
                                    # Base64로 인코딩
                                    base64_image = base64.b64encode(image_data).decode('utf-8')
                                    content_type = artifact.get('content_type', img_response.get('ContentType', 'image/jpeg'))
                                    
                                    html += f"""            <div class="image-container">
                <img src="data:{content_type};base64,{base64_image}" alt="{artifact['description']}">
                <div class="image-caption">{artifact['description']}</div>
            </div>
"""
                                except Exception as e:
                                    print(f"이미지 로드 실패: {s3_uri}, 오류: {str(e)}")
                                    html += f"            <p><em>이미지를 찾을 수 없습니다: {artifact['description']}</em></p>\n"
                                    base64_image = base64.b64encode(image_data).decode('utf-8')
                                    content_type = artifact.get('content_type', img_response.get('ContentType', 'image/jpeg'))
                                    
                                    html += f"""            <div class="image-container">
                <img src="data:{content_type};base64,{base64_image}" alt="{artifact['description']}">
                <div class="image-caption">{artifact['description']}</div>
            </div>
"""
                                except Exception as e:
                                    print(f"이미지 로드 실패: {s3_uri}, 오류: {str(e)}")
                                    html += f"            <p><em>이미지를 찾을 수 없습니다: {artifact['description']}</em></p>\n"
                            except Exception as e:
                                print(f"이미지 처리 중 오류 발생: {str(e)}")
                                html += f"            <p><em>이미지 처리 중 오류 발생: {artifact['description']}</em></p>\n"
                                    
                                # 경로에서 파일명만 추출
                                filename = img_key.split('/')[-1]
                                
                                # 다양한 경로 패턴 시도
                                alternative_paths = [
                                    f"images/{filename}",
                                    f"reports/images/{filename}",
                                    f"data/images/{filename}"
                                ]
                                
                                image_found = False
                                for alt_path in alternative_paths:
                                    try:
                                        print(f"대체 경로 시도: {img_bucket}/{alt_path}")
                                        img_response = s3_client.get_object(Bucket=img_bucket, Key=alt_path)
                                        image_data = img_response['Body'].read()
                                        img_key = alt_path  # 성공한 경로로 업데이트
                                        image_found = True
                                        print(f"대체 경로에서 이미지 찾음: {alt_path}")
                                        break
                                    except Exception:
                                        continue
                                
                                if not image_found:
                                    raise Exception(f"이미지를 찾을 수 없습니다: {s3_uri}")
                                
                                # 이미지 타입 결정
                                content_type = img_response.get('ContentType', '')
                                if not content_type or content_type == 'binary/octet-stream':
                                    # 파일 확장자로 콘텐츠 타입 추정
                                    if img_key.lower().endswith('.jpg') or img_key.lower().endswith('.jpeg'):
                                        content_type = 'image/jpeg'
                                    elif img_key.lower().endswith('.png'):
                                        content_type = 'image/png'
                                    elif img_key.lower().endswith('.gif'):
                                        content_type = 'image/gif'
                                    else:
                                        content_type = 'image/jpeg'  # 기본값
                                
                                # Base64로 인코딩
                                base64_image = base64.b64encode(image_data).decode('utf-8')
                                
                                print(f"이미지 로드 성공: {len(image_data)} 바이트, 콘텐츠 타입: {content_type}")
                                
                                html += f"""            <div class="image-container">
                <img src="data:{content_type};base64,{base64_image}" alt="{artifact['description']}">
                <div class="image-caption">{artifact['description']}</div>
            </div>
"""
                            except Exception as e:
                                print(f"이미지 로드 실패: {s3_uri}, 오류: {str(e)}")
                                traceback.print_exc()
                                html += f"            <p><em>이미지 로드 실패: {s3_uri} - {str(e)}</em></p>\n"
                        # path 필드를 사용하여 이미지 추가 (s3_uri가 없는 경우)
                        elif 'path' in artifact and (artifact['path'].lower().endswith('.jpg') or 
                                                   artifact['path'].lower().endswith('.jpeg') or 
                                                   artifact['path'].lower().endswith('.png') or 
                                                   artifact['path'].lower().endswith('.gif')):
                            print(f"분석 {i+1}, 아티팩트 {j+1}: 이미지 경로 발견 - {artifact['path']}")
                            
                            # S3 URI 파싱
                            s3_uri = artifact['path']
                            if s3_uri.startswith('s3://'):
                                s3_uri = s3_uri[5:]  # 's3://' 제거
                            
                            parts = s3_uri.split('/', 1)
                            img_bucket = parts[0]
                            img_key = parts[1] if len(parts) > 1 else ''
                            
                            # S3 클라이언트 생성
                            s3_client = boto3.client('s3')
                            
                            try:
                                # S3에서 이미지 파일 로드
                                try:
                                    print(f"S3에서 이미지 로드 시도: {img_bucket}/{img_key}")
                                    img_response = s3_client.get_object(Bucket=img_bucket, Key=img_key)
                                    image_data = img_response['Body'].read()
                                    
                                    # 이미지 타입 결정
                                    content_type = img_response.get('ContentType', '')
                                    if not content_type or content_type == 'binary/octet-stream':
                                        # 파일 확장자로 콘텐츠 타입 추정
                                        if img_key.lower().endswith('.jpg') or img_key.lower().endswith('.jpeg'):
                                            content_type = 'image/jpeg'
                                        elif img_key.lower().endswith('.png'):
                                            content_type = 'image/png'
                                        elif img_key.lower().endswith('.gif'):
                                            content_type = 'image/gif'
                                        else:
                                            content_type = 'image/jpeg'  # 기본값
                                    
                                    # Base64로 인코딩
                                    base64_image = base64.b64encode(image_data).decode('utf-8')
                                    
                                    print(f"이미지 로드 성공: {len(image_data)} 바이트, 콘텐츠 타입: {content_type}")
                                    
                                    html += f"""            <div class="image-container">
                <img src="data:{content_type};base64,{base64_image}" alt="{artifact['description']}">
                <div class="image-caption">{artifact['description']}</div>
            </div>
"""
                                except Exception as e:
                                    print(f"이미지 로드 실패: {s3_uri}, 오류: {str(e)}")
                                    html += f"            <p><em>이미지를 찾을 수 없습니다: {artifact['description']}</em></p>\n"
                                    content_type = img_response.get('ContentType', '')
                                    if not content_type or content_type == 'binary/octet-stream':
                                        # 파일 확장자로 콘텐츠 타입 추정
                                        if img_key.lower().endswith('.jpg') or img_key.lower().endswith('.jpeg'):
                                            content_type = 'image/jpeg'
                                        elif img_key.lower().endswith('.png'):
                                            content_type = 'image/png'
                                        elif img_key.lower().endswith('.gif'):
                                            content_type = 'image/gif'
                                        else:
                                            content_type = 'image/jpeg'  # 기본값
                                    
                                    # Base64로 인코딩
                                    base64_image = base64.b64encode(image_data).decode('utf-8')
                                    
                                    print(f"이미지 로드 성공: {len(image_data)} 바이트, 콘텐츠 타입: {content_type}")
                                    
                                    html += f"""            <div class="image-container">
                <img src="data:{content_type};base64,{base64_image}" alt="{artifact['description']}">
                <div class="image-caption">{artifact['description']}</div>
            </div>
"""
                                except Exception as e:
                                    print(f"이미지 로드 실패: {s3_uri}, 오류: {str(e)}")
                                    html += f"            <p><em>이미지를 찾을 수 없습니다: {artifact['description']}</em></p>\n"
                            except Exception as e:
                                print(f"이미지 처리 중 오류 발생: {str(e)}")
                                html += f"            <p><em>이미지 처리 중 오류 발생: {artifact['description']}</em></p>\n"
                                img_response = s3_client.get_object(Bucket=img_bucket, Key=img_key)
                                image_data = img_response['Body'].read()
                                
                                # 이미지 타입 결정
                                content_type = img_response.get('ContentType', '')
                                if not content_type or content_type == 'binary/octet-stream':
                                    # 파일 확장자로 콘텐츠 타입 추정
                                    if img_key.lower().endswith('.jpg') or img_key.lower().endswith('.jpeg'):
                                        content_type = 'image/jpeg'
                                    elif img_key.lower().endswith('.png'):
                                        content_type = 'image/png'
                                    elif img_key.lower().endswith('.gif'):
                                        content_type = 'image/gif'
                                    else:
                                        content_type = 'image/jpeg'  # 기본값
                                
                                # Base64로 인코딩
                                base64_image = base64.b64encode(image_data).decode('utf-8')
                                
                                print(f"이미지 로드 성공: {len(image_data)} 바이트, 콘텐츠 타입: {content_type}")
                                
                                html += f"""            <div class="image-container">
            <img src="data:{content_type};base64,{base64_image}" alt="{artifact['description']}">
            <div class="image-caption">{artifact['description']}</div>
        </div>
"""
                            except Exception as e:
                                print(f"이미지 로드 실패: {s3_uri}, 오류: {str(e)}")
                                html += f"            <p><em>이미지를 찾을 수 없습니다: {artifact['description']}</em></p>\n"
                            except Exception as e:
                                print(f"이미지 처리 중 오류 발생: {str(e)}")
                                html += f"            <p><em>이미지 처리 중 오류 발생: {artifact['description']}</em></p>\n"
                            except Exception as e:
                                print(f"이미지 로드 실패: {s3_uri}, 오류: {str(e)}")
                                traceback.print_exc()
                                html += f"            <p><em>이미지 로드 실패: {s3_uri} - {str(e)}</em></p>\n"
                    except Exception as e:
                        print(f"분석 {i+1}, 아티팩트 {j+1} 추가 중 오류: {str(e)}")
                        print(f"아티팩트 내용: {artifact}")
                        traceback.print_exc()
                
                html += "        </div>\n"
            
            html += "    </div>\n"
        except Exception as e:
            print(f"분석 {i+1} 상세 내용 추가 중 오류: {str(e)}")
            print(f"분석 내용: {analysis}")
            traceback.print_exc()
    
    # 결론 섹션 추가
    print("결론 섹션 추가")
    html += f"""    <h2>{t['conclusions']}</h2>
    <div class="content">
        <p>분석 결과를 종합하면, 다음과 같은 결론을 내릴 수 있습니다:</p>
        <ul>
"""
    
    # 각 분석에서 주요 결론 추출
    for i, analysis in enumerate(analyses):
        try:
            print(f"분석 {i+1} 결론 추출: {analysis['name']}")
            # 결과 텍스트에서 주요 문장 추출 (마지막 문장 또는 첫 문장) 
            result_text = analysis['results']
            sentences = re.split(r'(?<=[.!?])\s+', result_text)
            
            if sentences:
                conclusion = sentences[-1] if len(sentences) > 1 else sentences[0]
                html += f"            <li>{conclusion}</li>\n"
        except Exception as e:
            print(f"분석 {i+1} 결론 추출 중 오류: {str(e)}")
            traceback.print_exc()
    
    # HTML 푸터 추가
    html += """        </ul>
    </div>
</body>
</html>"""
    
    print(f"HTML 보고서 생성 완료: {len(html)} 문자")
    return html.encode('utf-8'), 'text/html'

def generate_markdown_report(analyses, report_title, language='ko'):
    """
    분석 결과를 기반으로 마크다운 보고서를 생성합니다.
    
    Parameters:
    - analyses: 분석 결과 목록
    - report_title: 보고서 제목
    - language: 보고서 언어 ('ko' 또는 'en')
    
    Returns:
    - 마크다운 보고서 내용 및 콘텐츠 타입
    """
    print(f"generate_markdown_report 함수 시작: title={report_title}, language={language}")
    print(f"analyses 타입: {type(analyses)}, 길이: {len(analyses) if isinstance(analyses, list) else 'N/A'}")
    
    # 언어에 따른 텍스트 설정
    texts = {
        'ko': {
            'summary': '요약',
            'key_findings': '주요 발견사항',
            'detailed_analysis': '상세 분석',
            'conclusions': '결론 및 권장사항',
            'execution_time': '실행 시간',
            'no_artifacts': '생성된 아티팩트 없음',
            'generated_files': '생성된 파일'
        },
        'en': {
            'summary': 'Summary',
            'key_findings': 'Key Findings',
            'detailed_analysis': 'Detailed Analysis',
            'conclusions': 'Conclusions & Recommendations',
            'execution_time': 'Execution Time',
            'no_artifacts': 'No artifacts generated',
            'generated_files': 'Generated Files'
        }
    }
    
    # 기본 언어를 한국어로 설정
    t = texts.get(language, texts['ko'])
    
    # 마크다운 헤더 생성
    md = f"# {report_title}\n\n"
    
    # 요약 섹션
    md += f"## {t['summary']}\n\n"
    md += f"이 보고서는 {len(analyses)}개의 분석 단계에서 생성된 결과를 종합한 것입니다.\n\n"
    
    # 주요 발견사항 섹션
    md += f"## {t['key_findings']}\n\n"
    for i, analysis in enumerate(analyses):
        try:
            print(f"분석 {i+1} 발견사항 추가: {analysis['name']}")
            md += f"- **{analysis['name']}**: {analysis['results']}\n"
        except Exception as e:
            print(f"분석 {i+1} 발견사항 추가 중 오류: {str(e)}")
            traceback.print_exc()
    
    md += f"\n## {t['detailed_analysis']}\n\n"
    
    # 각 분석 단계에 대한 상세 내용 추가
    for i, analysis in enumerate(analyses):
        try:
            print(f"분석 {i+1} 상세 내용 추가: {analysis['name']}")
            md += f"### {analysis['name']}\n\n"
            md += f"*{t['execution_time']}: {analysis['time']}*\n\n"
            md += f"{analysis['results']}\n\n"
            
            md += f"#### {t['generated_files']}\n\n"
            
            if not analysis['artifacts']:
                print(f"분석 {i+1}: 아티팩트 없음")
                md += f"{t['no_artifacts']}\n\n"
            else:
                print(f"분석 {i+1}: {len(analysis['artifacts'])}개의 아티팩트 추가")
                for j, artifact in enumerate(analysis['artifacts']):
                    try:
                        print(f"분석 {i+1}, 아티팩트 {j+1} 추가: {artifact['path']}")
                        md += f"- **{artifact['path']}**: {artifact['description']}\n"
                        
                        # 이미지 S3 URI가 있는 경우 이미지 참조 추가
                        if 's3_uri' in artifact:
                            print(f"분석 {i+1}, 아티팩트 {j+1}: 이미지 S3 URI 참조 추가")
                            s3_uri = artifact['s3_uri']
                            md += f"  *이미지 파일: {s3_uri}*\n\n"
                        # path 필드를 사용하여 이미지 참조 추가 (s3_uri가 없는 경우)
                        elif 'path' in artifact and (artifact['path'].lower().endswith('.jpg') or 
                                                   artifact['path'].lower().endswith('.jpeg') or 
                                                   artifact['path'].lower().endswith('.png') or 
                                                   artifact['path'].lower().endswith('.gif')):
                            print(f"분석 {i+1}, 아티팩트 {j+1}: 이미지 경로 참조 추가 - {artifact['path']}")
                            md += f"  *이미지 파일: {artifact['path']}*\n\n"
                    except Exception as e:
                        print(f"분석 {i+1}, 아티팩트 {j+1} 추가 중 오류: {str(e)}")
                        traceback.print_exc()
            
            md += "\n"
        except Exception as e:
            print(f"분석 {i+1} 상세 내용 추가 중 오류: {str(e)}")
            traceback.print_exc()
    
    # 결론 섹션 추가
    md += f"## {t['conclusions']}\n\n"
    md += "분석 결과를 종합하면, 다음과 같은 결론을 내릴 수 있습니다:\n\n"
    
    # 각 분석에서 주요 결론 추출
    for i, analysis in enumerate(analyses):
        try:
            print(f"분석 {i+1} 결론 추출: {analysis['name']}")
            # 결과 텍스트에서 주요 문장 추출 (마지막 문장 또는 첫 문장)
            result_text = analysis['results']
            sentences = re.split(r'(?<=[.!?])\s+', result_text)
            
            if sentences:
                conclusion = sentences[-1] if len(sentences) > 1 else sentences[0]
                md += f"- {conclusion}\n"
        except Exception as e:
            print(f"분석 {i+1} 결론 추출 중 오류: {str(e)}")
            traceback.print_exc()
    
    print(f"마크다운 보고서 생성 완료: {len(md)} 문자")
    return md.encode('utf-8'), 'text/markdown'

def convert_html_to_pdf(html_content, language='ko'):
    """
    HTML 내용을 PDF로 변환합니다.
    
    참고: Lambda 환경에서는 WeasyPrint 또는 다른 PDF 변환 라이브러리를 사용하기 위해
    추가 설정이 필요합니다. 이 함수는 실제 구현을 위한 예시입니다.
    
    Parameters:
    - html_content: HTML 내용 (바이트)
    - language: 보고서 언어 ('ko' 또는 'en')
    
    Returns:
    - PDF 내용 (바이트)
    """
    print(f"convert_html_to_pdf 함수 시작: HTML 길이={len(html_content)} 바이트")
    try:
        # 실제 구현에서는 WeasyPrint 또는 다른 PDF 변환 라이브러리를 사용
        # 이 예시에서는 HTML 내용을 그대로 반환
        print("PDF 변환 라이브러리가 구현되지 않았습니다. HTML 내용을 그대로 반환합니다.")
        return html_content
    except Exception as e:
        print(f"PDF 변환 중 오류 발생: {str(e)}")
        traceback.print_exc()
        # 오류 발생 시 HTML 내용을 그대로 반환
        return html_content

def lambda_handler(event, context):
    """
    Lambda 함수: 분석 결과를 기반으로 보고서를 생성하는 함수의 핸들러
    
    Parameters:
    - event: Lambda 이벤트 객체
    - context: Lambda 컨텍스트 객체
    
    Returns:
    - 생성된 보고서 파일의 S3 URL을 포함하는 JSON 응답
    """
    print("lambda_handler 함수 시작")
    print(f"이벤트: {json.dumps(event)}")
    
    try:
        action_group = event.get('actionGroup', '')
        message_version = event.get('messageVersion', '')
        function = event.get('function', '')
        
        print(f"액션 그룹: {action_group}, 메시지 버전: {message_version}, 함수: {function}")
        
        if function == 'generate_report':
            # 파라미터 추출
            s3_uri = get_named_parameter(event, "s3_uri")
            analyses_param = get_named_parameter(event, "analyses") or []
            report_format = get_named_parameter(event, "report_format") or 'html'
            report_title = get_named_parameter(event, "report_title") or '분석 보고서'
            report_language = get_named_parameter(event, "report_language") or 'ko'
            
            print(f"파라미터: s3_uri={s3_uri}, report_format={report_format}, report_title={report_title}")
            print(f"analyses 타입: {type(analyses_param)}, 길이: {len(analyses_param) if isinstance(analyses_param, list) else (len(analyses_param) if isinstance(analyses_param, str) else 'N/A')}")
            
            # analyses 파라미터 처리 강화
            print(f"analyses_param 타입: {type(analyses_param)}")
            
            # 문자열로 전달된 경우 파싱 시도
            if isinstance(analyses_param, str):
                print(f"analyses는 문자열입니다. 파싱 시도...")
                try:
                    # JSON 파싱 시도
                    analyses_param = json.loads(analyses_param)
                    print("analyses를 JSON에서 파싱했습니다.")
                except json.JSONDecodeError:
                    print("JSON 파싱 실패, Python 객체 표현 파싱 시도...")
                    try:
                        # Python 객체 표현 파싱 시도
                        # 문자열 내의 작은따옴표를 큰따옴표로 변환하여 JSON 형식으로 만들기
                        analyses_str = analyses_param.replace("'", "\"")
                        # name=value 형식을 "name":"value" 형식으로 변환
                        analyses_str = re.sub(r'(\w+)=', r'"\1":', analyses_str)
                        try:
                            analyses_param = json.loads(analyses_str)
                            print("수정된 문자열을 JSON으로 파싱했습니다.")
                        except json.JSONDecodeError:
                            # 여전히 실패하면 일반 텍스트로 처리
                            print("JSON 파싱 실패, 일반 텍스트로 처리합니다.")
                            
                            # 텍스트를 분석 항목으로 변환
                            sections = re.split(r'\n\n+', analyses_param)
                            analyses_list = []
                            
                            for section in sections:
                                if not section.strip():
                                    continue
                                    
                                # 섹션 제목과 내용 분리
                                parts = section.split(':', 1)
                                if len(parts) == 2:
                                    name = parts[0].strip()
                                    results = parts[1].strip()
                                    
                                    # 분석 항목 생성
                                    analysis_item = {
                                        "name": name,
                                        "time": datetime.now().strftime("%Y-%m-%d"),
                                        "results": results,
                                        "references": [],
                                        "artifacts": []
                                    }
                                    
                                    analyses_list.append(analysis_item)
                            
                            if analyses_list:
                                analyses_param = analyses_list
                                print(f"텍스트를 {len(analyses_list)}개의 분석 항목으로 변환했습니다.")
                            else:
                                print("텍스트에서 분석 항목을 추출할 수 없습니다.")
                                analyses_param = []
                    except Exception as e:
                        print(f"analyses 파싱 오류: {str(e)}")
                        traceback.print_exc()
                        
                        # 파싱 실패 시 텍스트를 단일 분석 항목으로 변환
                        analyses_param = [{
                            "name": "Analysis Results",
                            "time": datetime.now().strftime("%Y-%m-%d"),
                            "results": analyses_param,
                            "references": [],
                            "artifacts": []
                        }]
                        print("텍스트를 단일 분석 항목으로 변환했습니다.")
            # 딕셔너리인 경우 리스트로 변환
            elif isinstance(analyses_param, dict):
                print("analyses는 딕셔너리입니다. 리스트로 변환합니다.")
                analyses_param = [analyses_param]
            # 리스트가 아닌 경우 빈 리스트로 초기화
            elif not isinstance(analyses_param, list):
                print(f"analyses가 예상치 못한 타입입니다: {type(analyses_param)}. 빈 리스트로 초기화합니다.")
                analyses_param = []
            
            # analyses가 리스트인지 확인 (이 부분은 이제 필요 없음 - 위에서 모든 경우를 처리했기 때문)
            # 대신 analyses_param이 비어있는지 확인
            if not analyses_param:
                print("analyses 파라미터가 비어 있습니다.")
                return {
                    'response': {
                        'actionGroup': action_group,
                        'function': function,
                        'functionResponse': {
                            'responseBody': {'TEXT': {'body': json.dumps({'error': 'analyses 파라미터가 비어 있습니다.'}, ensure_ascii=False)}}
                        }
                    },
                    'messageVersion': message_version
                }
            
            # analyses 객체 구조 수정
            analyses = []
            for analysis in analyses_param:
                print(f"분석 항목 처리: {type(analysis)}")
                
                # 문자열로 전달된 필드 처리
                if isinstance(analysis, str):
                    try:
                        # 문자열 내의 작은따옴표를 큰따옴표로 변환하여 JSON 형식으로 만들기
                        analysis_str = analysis.replace("'", "\"")
                        # name=value 형식을 "name":"value" 형식으로 변환
                        analysis_str = re.sub(r'(\w+)=', r'"\1":', analysis_str)
                        try:
                            analysis = json.loads(analysis_str)
                            print("분석 항목을 JSON으로 파싱했습니다.")
                        except json.JSONDecodeError:
                            try:
                                analysis = ast.literal_eval(analysis)
                                print("분석 항목을 Python 객체로 파싱했습니다.")
                            except Exception as e:
                                print(f"분석 항목 파싱 실패: {analysis}, 오류: {str(e)}")
                                continue
                    except Exception as e:
                        print(f"분석 항목 파싱 실패: {analysis}, 오류: {str(e)}")
                        continue
                
                # 필드 추출 및 정리
                name = analysis.get('name', '')
                time = analysis.get('time', datetime.now().strftime("%Y-%m-%d"))  # 시간이 없으면 현재 시간 사용
                results = analysis.get('results', '')
                
                # 필수 필드 확인
                if not name or not results:
                    print(f"필수 필드가 없는 분석 결과: {analysis}")
                    continue
                
                # references와 artifacts 필드 처리
                references = []
                artifacts = []
                
                # references 필드 처리
                if 'references' in analysis:
                    if isinstance(analysis['references'], list):
                        references = analysis['references']
                    elif isinstance(analysis['references'], str):
                        try:
                            # 문자열 내의 작은따옴표를 큰따옴표로 변환하여 JSON 형식으로 만들기
                            refs_str = analysis['references'].replace("'", "\"")
                            # name=value 형식을 "name":"value" 형식으로 변환
                            refs_str = re.sub(r'(\w+)=', r'"\1":', refs_str)
                            try:
                                references = json.loads(refs_str)
                                print("references를 JSON으로 파싱했습니다.")
                            except json.JSONDecodeError:
                                try:
                                    references = ast.literal_eval(analysis['references'])
                                    print("references를 Python 객체로 파싱했습니다.")
                                except Exception as e:
                                    print(f"references 파싱 실패: {analysis['references']}, 오류: {str(e)}")
                        except Exception as e:
                            print(f"references 파싱 실패: {analysis['references']}, 오류: {str(e)}")
                
                # artifacts 필드 처리
                if 'artifacts' in analysis:
                    if isinstance(analysis['artifacts'], list):
                        artifacts = analysis['artifacts']
                    elif isinstance(analysis['artifacts'], str):
                        try:
                            # 문자열 내의 작은따옴표를 큰따옴표로 변환하여 JSON 형식으로 만들기
                            arts_str = analysis['artifacts'].replace("'", "\"")
                            # name=value 형식을 "name":"value" 형식으로 변환
                            arts_str = re.sub(r'(\w+)=', r'"\1":', arts_str)
                            try:
                                artifacts = json.loads(arts_str)
                                print("artifacts를 JSON으로 파싱했습니다.")
                            except json.JSONDecodeError:
                                try:
                                    artifacts = ast.literal_eval(analysis['artifacts'])
                                    print("artifacts를 Python 객체로 파싱했습니다.")
                                except Exception as e:
                                    print(f"artifacts 파싱 실패: {analysis['artifacts']}, 오류: {str(e)}")
                        except Exception as e:
                            print(f"artifacts 파싱 실패: {analysis['artifacts']}, 오류: {str(e)}")
                
                # 정리된 객체 추가
                cleaned_analysis = {
                    'name': name,
                    'time': time,
                    'results': results,
                    'references': references,
                    'artifacts': artifacts
                }
                
                print(f"정리된 분석 항목: {cleaned_analysis['name']}")
                analyses.append(cleaned_analysis)
            
            # 분석 결과가 비어있는지 확인
            if not analyses:
                print("분석 결과가 비어 있습니다.")
                return {
                    'response': {
                        'actionGroup': action_group,
                        'function': function,
                        'functionResponse': {
                            'responseBody': {'TEXT': {'body': json.dumps({'error': '분석 결과가 제공되지 않았습니다.'}, ensure_ascii=False)}}
                        }
                    },
                    'messageVersion': message_version
                }
            
            print(f"정리된 analyses: {json.dumps(analyses, ensure_ascii=False)[:500]}...")
            
            # 함수 호출
            print("generate_report 함수 호출")
            output = generate_report(s3_uri, analyses, report_format, report_title, report_language)
            print(f"generate_report 함수 결과: {json.dumps(output, ensure_ascii=False)[:200]}...")
        else:
            print(f"지원되지 않는 함수: {function}")
            output = {
                'error': f"지원되지 않는 함수: {function}"
            }
        
        # Bedrock Agent 응답 형식으로 변환
        action_response = {
            'actionGroup': action_group,
            'function': function,
            'functionResponse': {
                'responseBody': {'TEXT': {'body': json.dumps(output, ensure_ascii=False)}}
            }
        }
        
        function_response = {'response': action_response, 'messageVersion': message_version}
        print(f"응답 생성 완료: {json.dumps(function_response, ensure_ascii=False)[:200]}...")
        return function_response
    
    except Exception as e:
        print(f"lambda_handler 함수 처리 중 오류 발생: {str(e)}")
        traceback.print_exc()
        
        # 오류 발생 시에도 Bedrock Agent 응답 형식으로 반환
        error_response = {
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'function': event.get('function', ''),
                'functionResponse': {
                    'responseBody': {'TEXT': {'body': json.dumps({'error': f"처리 중 오류가 발생했습니다: {str(e)}"}, ensure_ascii=False)}}
                }
            },
            'messageVersion': event.get('messageVersion', '')
        }
        return error_response
