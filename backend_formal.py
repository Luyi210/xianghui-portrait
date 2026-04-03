from __future__ import annotations

import os
from typing import Dict, List, Optional

import httpx
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

app = FastAPI(title='相辉学堂人物画像系统（正式版骨架）')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_FILE = os.path.join(BASE_DIR, 'formal_student_data.csv')
HTML_PAGES = {
    'index_formal.html',
    'student_formal.html',
    'benchmark_overview.html',
    'benchmark_compare.html',
    'benchmark_detail.html',
    'resources_fudan.html',
    'policy_overview.html',
    'data_methodology.html',
}
MARKDOWN_FILES = {
    'phase1_plan.md',
    'phase2_progress.md',
    'phase3_progress.md',
    'PROJECT_FILE_GUIDE.md',
    'UPDATE_WEBSITE_WORKFLOW.md',
    'DEPLOY_RENDER.md',
}
PUBLIC_DOC_FILES = {
    'benchmark_schema.csv',
}
DIMENSION_LABELS = {
    'dim_academic_interest': '学术志趣',
    'dim_resilience': '学业韧性',
    'dim_innovation': '创新人格',
    'dim_learning_motivation': '学习动力',
    'dim_research_engagement': '科研参与',
    'dim_mentorship': '导学关系',
    'dim_environment_satisfaction': '环境满意度',
    'dim_mental_health': '心理健康',
}
RISK_LABELS = {
    'risk_psychology': '心理健康风险',
    'risk_no_mentor': '导师缺失风险',
    'risk_low_interest': '学术志趣不足风险',
    'risk_low_research': '科研参与不足风险',
    'risk_external_driven': '外驱主导风险',
    'risk_low_ai_usage': 'AI 使用不足风险',
    'risk_overload': '学业负担过高风险',
}
AI_PROVIDER = os.getenv('AI_PROVIDER', '').strip().lower()
AI_API_KEY = os.getenv('AI_API_KEY', '').strip()
AI_BASE_URL = os.getenv('AI_BASE_URL', '').strip()
AI_MODEL = os.getenv('AI_MODEL', '').strip()
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip()
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat').strip()


def normalize_base_url(url: str) -> str:
    return url.rstrip('/')


def build_openai_client():
    api_key = AI_API_KEY or DEEPSEEK_API_KEY
    if not api_key:
        return None
    base_url = AI_BASE_URL or 'https://api.deepseek.com'
    try:
        return OpenAI(api_key=api_key, base_url=normalize_base_url(base_url))
    except Exception:
        return None


client = build_openai_client() if AI_PROVIDER in ('', 'openai') or DEEPSEEK_API_KEY else None


_df_cache: Optional[pd.DataFrame] = None
_df_mtime: Optional[float] = None


def public_file_response(relative_path: str) -> FileResponse:
    file_path = os.path.join(BASE_DIR, relative_path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail='文件不存在')
    return FileResponse(file_path)


def active_ai_config() -> Dict[str, str]:
    if AI_PROVIDER:
        return {
            'provider': AI_PROVIDER,
            'api_key': AI_API_KEY,
            'base_url': AI_BASE_URL,
            'model': AI_MODEL,
        }
    return {
        'provider': 'openai' if DEEPSEEK_API_KEY else '',
        'api_key': DEEPSEEK_API_KEY,
        'base_url': 'https://api.deepseek.com' if DEEPSEEK_API_KEY else '',
        'model': DEEPSEEK_MODEL if DEEPSEEK_API_KEY else '',
    }


async def ask_openai_compatible(system_prompt: str, user_prompt: str, model: str) -> str:
    if client is None:
        raise RuntimeError('OpenAI compatible client 未初始化')
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        stream=False,
    )
    return resp.choices[0].message.content or ''


async def ask_anthropic_compatible(system_prompt: str, user_prompt: str, base_url: str, api_key: str, model: str) -> str:
    endpoint = f"{normalize_base_url(base_url)}/v1/messages"
    payload = {
        'model': model,
        'max_tokens': 1024,
        'system': system_prompt,
        'messages': [
            {'role': 'user', 'content': user_prompt},
        ],
    }
    headers = {
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
    }
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resp = await http_client.post(endpoint, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    parts = data.get('content', [])
    text_parts = [part.get('text', '') for part in parts if isinstance(part, dict) and part.get('type') == 'text']
    answer = ''.join(text_parts).strip()
    if not answer:
        raise RuntimeError('Anthropic compatible 接口返回中未找到文本内容')
    return answer


if os.path.isdir(ASSETS_DIR):
    app.mount('/assets', StaticFiles(directory=ASSETS_DIR), name='assets')


@app.get('/', include_in_schema=False)
def frontend_root():
    return public_file_response('index_formal.html')


@app.get('/{page_name}.html', include_in_schema=False)
def frontend_page(page_name: str):
    filename = f'{page_name}.html'
    if filename not in HTML_PAGES:
        raise HTTPException(status_code=404, detail='页面不存在')
    return public_file_response(filename)


@app.get('/1.jpeg', include_in_schema=False)
def frontend_background_image():
    return public_file_response('1.jpeg')


@app.get('/{doc_name}.md', include_in_schema=False)
def frontend_markdown_file(doc_name: str):
    filename = f'{doc_name}.md'
    if filename not in MARKDOWN_FILES:
        raise HTTPException(status_code=404, detail='文件不存在')
    return public_file_response(os.path.join('docs', filename))


@app.get('/docs/{file_name}', include_in_schema=False)
def frontend_doc_file(file_name: str):
    if file_name not in PUBLIC_DOC_FILES:
        raise HTTPException(status_code=404, detail='文件不存在')
    return public_file_response(os.path.join('docs', file_name))


def load_df() -> pd.DataFrame:
    global _df_cache, _df_mtime
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    mtime = os.path.getmtime(DATA_FILE)
    if _df_cache is None or mtime != _df_mtime:
        _df_cache = pd.read_csv(DATA_FILE)
        _df_mtime = mtime
    return _df_cache.copy()


def grade_reference(df: pd.DataFrame, grade: int) -> pd.DataFrame:
    sub = df[df['grade'] == grade]
    return sub if not sub.empty else df


def dim_payload(row: pd.Series) -> List[Dict]:
    items = []
    for key, label in DIMENSION_LABELS.items():
        items.append({
            'key': key,
            'label': label,
            'score': round(float(row[key]), 2),
            'percentile': round(float(row[f'pct_{key}']), 2),
            'z_score': round(float(row[f'z_{key}']), 4),
            'zone': '优势区' if row[f'pct_{key}'] >= 75 else '关注区' if row[f'pct_{key}'] <= 25 else '常态区'
        })
    return items


def risk_payload(row: pd.Series) -> List[Dict]:
    items = []
    descriptions = {
        'risk_psychology': '心理健康自评偏低，且近期压力/负担感较高。',
        'risk_no_mentor': '当前尚未建立稳定导师支持关系，且年级已进入更需要指导的阶段。',
        'risk_low_interest': '当前专业认同、学术目标或学术志向不足，方向感偏弱。',
        'risk_low_research': '当前科研参与程度较浅，尚未形成稳定研究投入。',
        'risk_external_driven': '学习动力偏向外部评价驱动，内在兴趣支持不足。',
        'risk_low_ai_usage': '较少使用 AI 辅助学习/科研，可能错失提效机会。',
        'risk_overload': '当前学业负担与压力明显偏高，正在压缩恢复空间。',
    }
    for key, label in RISK_LABELS.items():
        if int(row.get(key, 0)) == 1:
            items.append({
                'key': key,
                'label': label,
                'severity': row.get(f'{key}_severity', 'none'),
                'description': descriptions.get(key, '')
            })
    order = {'red': 0, 'yellow': 1, 'green': 2, 'none': 3}
    items.sort(key=lambda x: order.get(x['severity'], 9))
    return items


def build_growth_series(row: pd.Series) -> Dict[str, List]:
    labels = ['入学前', '大一', '大二', '大三', '当前']
    current = {
        '学术志趣': float(row['dim_academic_interest']),
        '科研参与': float(row['dim_research_engagement']),
        '心理健康': float(row['dim_mental_health']),
        '导学关系': float(row['dim_mentorship']),
    }
    base_shift = {
        1: [10, 12, 4, 6],
        2: [8, 9, 5, 5],
        3: [6, 7, 6, 4],
        4: [5, 6, 7, 4],
    }
    shifts = base_shift.get(int(row['grade']), [7, 8, 5, 5])
    series = {}
    keys = list(current.keys())
    for idx, key in enumerate(keys):
        end = current[key]
        start = max(20, end - shifts[idx] - np.random.uniform(6, 14))
        middle1 = start + (end - start) * np.random.uniform(0.35, 0.48)
        middle2 = start + (end - start) * np.random.uniform(0.58, 0.72)
        middle3 = start + (end - start) * np.random.uniform(0.78, 0.92)
        values = [start, middle1, middle2, middle3, end]
        if key == '心理健康' and row['warning_level'] in ['red', 'yellow']:
            values[2] = min(values[2], values[1] + np.random.uniform(-4, 3))
            values[3] = min(values[3], values[2] + np.random.uniform(-3, 4))
        series[key] = [round(float(np.clip(v, 0, 100)), 2) for v in values]
    return {'labels': labels, 'series': series}


def filter_df(
    df: pd.DataFrame,
    grade: Optional[int] = None,
    student_type: Optional[str] = None,
    warning_level: Optional[str] = None,
    major_track: Optional[str] = None,
) -> pd.DataFrame:
    if grade is not None:
        df = df[df['grade'] == grade]
    if student_type:
        df = df[df['student_type'] == student_type]
    if warning_level:
        df = df[df['warning_level'] == warning_level]
    if major_track:
        df = df[df['major_track'] == major_track]
    return df


def dataset_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return '暂无数据。'
    type_dist = df['student_type'].value_counts().to_dict()
    warning_dist = df['warning_level'].value_counts().to_dict()
    dims = {label: round(float(df[key].mean()), 2) for key, label in DIMENSION_LABELS.items()}
    grades = sorted(int(g) for g in df['grade'].dropna().unique().tolist()) if 'grade' in df.columns else []
    grade_text = f"；覆盖年级 {grades}" if grades else ''
    return (
        f"样本量 {len(df)}{grade_text}；类型分布 {type_dist}；预警分布 {warning_dist}；"
        f"八大维度均值 {dims}；导师覆盖率 {round(float((df['has_fixed_mentor'] > 0).mean() * 100), 2)}%；"
        f"科研参与率 {round(float((df['research_participation_level'] >= 60).mean() * 100), 2)}%；"
        f"FDUROP参与率 {round(float((df['fdurop_participated'] > 0).mean() * 100), 2)}%。"
    )


def student_context_text(row: pd.Series) -> str:
    strengths = []
    concerns = []
    dim_pairs = [
        ('学术志趣', float(row['dim_academic_interest'])),
        ('学业韧性', float(row['dim_resilience'])),
        ('创新人格', float(row['dim_innovation'])),
        ('学习动力', float(row['dim_learning_motivation'])),
        ('科研参与', float(row['dim_research_engagement'])),
        ('导学关系', float(row['dim_mentorship'])),
        ('环境满意度', float(row['dim_environment_satisfaction'])),
        ('心理健康', float(row['dim_mental_health'])),
    ]
    for label, score in dim_pairs:
        if score >= 70:
            strengths.append(label)
        elif score <= 50:
            concerns.append(label)
    return (
        f"学生 {row['name']}（学号 {int(row['student_id'])}），{int(row['grade'])} 年级，{row['major_track']} 方向，"
        f"类型 {row['student_type']}，置信度 {round(float(row['student_type_confidence']), 1)}%，"
        f"预警等级 {row['warning_level']}，问题摘要：{row['issue_summary']}。"
        f"优势维度：{strengths if strengths else ['暂无特别突出的单项优势']}；"
        f"关注维度：{concerns if concerns else ['整体较均衡']}。"
        f"八大维度：学术志趣 {round(float(row['dim_academic_interest']),2)}，学业韧性 {round(float(row['dim_resilience']),2)}，"
        f"创新人格 {round(float(row['dim_innovation']),2)}，学习动力 {round(float(row['dim_learning_motivation']),2)}，"
        f"科研参与 {round(float(row['dim_research_engagement']),2)}，导学关系 {round(float(row['dim_mentorship']),2)}，"
        f"环境满意度 {round(float(row['dim_environment_satisfaction']),2)}，心理健康 {round(float(row['dim_mental_health']),2)}。"
        f"建议路径：{row['advice_path']}"
    )


def build_type_compare(row: pd.Series) -> List[Dict]:
    prototypes = {
        '科研驱动型': {'学术志趣': 82, '科研参与': 86, '导学关系': 74, '心理健康': 57},
        '竞赛转型型': {'学术志趣': 68, '科研参与': 62, '导学关系': 56, '心理健康': 55},
        '均衡发展型': {'学术志趣': 67, '科研参与': 58, '导学关系': 61, '心理健康': 56},
        '压力应对型': {'学术志趣': 60, '科研参与': 54, '导学关系': 52, '心理健康': 39},
        '探索迷茫型': {'学术志趣': 42, '科研参与': 40, '导学关系': 46, '心理健康': 49},
    }
    me = {
        '学术志趣': float(row['dim_academic_interest']),
        '科研参与': float(row['dim_research_engagement']),
        '导学关系': float(row['dim_mentorship']),
        '心理健康': float(row['dim_mental_health']),
    }
    current_proto = prototypes.get(row['student_type'], prototypes['均衡发展型'])
    adjacent_proto = prototypes.get(row['adjacent_type'], prototypes['均衡发展型'])
    payload = []
    for label in ['学术志趣', '科研参与', '导学关系', '心理健康']:
        payload.append({
            'label': label,
            'mine': round(me[label], 2),
            'current_type_avg': current_proto[label],
            'adjacent_type_avg': adjacent_proto[label],
        })
    return payload


@app.get('/api/formal/overview')
def formal_overview(grade: Optional[int] = Query(default=None)):
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': 'formal_student_data.csv 不存在，请先运行 formal_data_generate.py'}

    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'error', 'message': '当前筛选条件下无数据'}

    dimensions = []
    for key, label in DIMENSION_LABELS.items():
        dimensions.append({
            'key': key,
            'label': label,
            'mean': round(float(df[key].mean()), 2),
            'std': round(float(df[key].std(ddof=0)), 2),
        })

    warning_counts = df['warning_level'].value_counts().to_dict()
    type_distribution = df['student_type'].value_counts().to_dict()
    mentor_coverage = round(float((df['has_fixed_mentor'] > 0).mean() * 100), 2)
    research_rate = round(float((df['research_participation_level'] >= 60).mean() * 100), 2)
    fdurop_rate = round(float((df['fdurop_participated'] > 0).mean() * 100), 2)
    pnp_rate = round(float((df['pnp_used'] > 0).mean() * 100), 2)
    avg_mental = round(float(df['dim_mental_health'].mean()), 2)

    return {
        'status': 'success',
        'summary': {
            'total_students': int(len(df)),
            'current_grade': grade,
            'mentor_coverage_rate': mentor_coverage,
            'research_participation_rate': research_rate,
            'fdurop_participation_rate': fdurop_rate,
            'pnp_usage_rate': pnp_rate,
            'avg_mental_health': avg_mental,
        },
        'dimensions': dimensions,
        'type_distribution': type_distribution,
        'warning_distribution': warning_counts,
    }


@app.get('/api/formal/students')
def formal_students(
    grade: Optional[int] = None,
    student_type: Optional[str] = None,
    warning_level: Optional[str] = None,
    major_track: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200)
):
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}

    df = filter_df(df, grade=grade, student_type=student_type, warning_level=warning_level, major_track=major_track)

    cols = ['student_id', 'name', 'grade', 'major_track', 'source_province', 'student_type', 'warning_level', 'warning_count']
    records = df.sort_values(['warning_count', 'student_type_confidence'], ascending=[False, False])[cols].head(limit).to_dict('records')
    return {'status': 'success', 'records': records, 'total': int(len(df)), 'grade': grade}


@app.get('/api/formal/student/{student_id}')
def formal_student_detail(student_id: int):
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}

    sub = df[df['student_id'] == student_id]
    if sub.empty:
        return {'status': 'error', 'message': '未找到该学生'}

    row = sub.iloc[0]
    ref = grade_reference(df, int(row['grade']))
    avg_scores = [round(float(ref[k].mean()), 2) for k in DIMENSION_LABELS.keys()]

    return {
        'status': 'success',
        'basic': {
            'student_id': int(row['student_id']),
            'name': row['name'],
            'gender': row['gender'],
            'grade': int(row['grade']),
            'major_track': row['major_track'],
            'admission_type': row['admission_type'],
            'source_province': row['source_province'],
            'source_region_type': row['source_region_type'],
            'high_school_level': row['high_school_level'],
            'family_class_score': int(row['family_class_score']),
        },
        'portrait': {
            'student_type': row['student_type'],
            'student_type_confidence': round(float(row['student_type_confidence']), 1),
            'adjacent_type': row['adjacent_type'],
            'type_features': row['type_features'],
            'warning_level': row['warning_level'],
            'warning_count': int(row['warning_count']),
        },
        'dimensions': dim_payload(row),
        'radar': {
            'labels': list(DIMENSION_LABELS.values()),
            'my_scores': [round(float(row[k]), 2) for k in DIMENSION_LABELS.keys()],
            'grade_avg_scores': avg_scores,
        },
        'issues': {
            'summary': row['issue_summary'],
            'risk_tags': risk_payload(row),
        },
        'advice': {
            'academic': row['advice_academic'],
            'psychology': row['advice_psychology'],
            'skill': row['advice_skill'],
            'resource': row['advice_resource'],
            'path': row['advice_path'],
            'benchmark_case': row['benchmark_case'],
        },
        'growth': build_growth_series(row),
        'type_compare': build_type_compare(row),
        'raw_signals': {
            'goal_clarity': round(float(row['goal_clarity']), 2),
            'mental_health_score': round(float(row['mental_health_score']), 2),
            'stress_level': round(float(row['stress_level']), 2),
            'research_participation_level': round(float(row['research_participation_level']), 2),
            'research_depth_score': round(float(row['research_depth_score']), 2),
            'has_fixed_mentor': bool(row['has_fixed_mentor'] > 0),
            'ai_use_frequency': round(float(row['ai_use_frequency']), 2),
            'pnp_used': bool(row['pnp_used'] > 0),
            'fdurop_participated': bool(row['fdurop_participated'] > 0),
        }
    }


@app.get('/api/formal/warnings')
def formal_warnings(
    grade: Optional[int] = None,
    limit: int = Query(default=50, ge=1, le=200)
):
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}

    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'success', 'records': [], 'grade': grade}

    order = {'red': 0, 'yellow': 1, 'green': 2, 'none': 3}
    ranked = df.copy()
    ranked['warning_order'] = ranked['warning_level'].map(order)
    ranked = ranked.sort_values(['warning_order', 'warning_count', 'student_type_confidence'], ascending=[True, False, False]).head(limit)

    records = []
    for _, row in ranked.iterrows():
        records.append({
            'student_id': int(row['student_id']),
            'name': row['name'],
            'grade': int(row['grade']),
            'major_track': row['major_track'],
            'warning_level': row['warning_level'],
            'warning_count': int(row['warning_count']),
            'student_type': row['student_type'],
            'issue_summary': row['issue_summary'],
        })
    return {'status': 'success', 'records': records}


@app.get('/api/formal/group_compare')
def formal_group_compare(
    group_by: str = Query(default='admission_type'),
    grade: Optional[int] = Query(default=None)
):
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    if group_by not in ['admission_type', 'major_track', 'source_region_type', 'warning_level', 'student_type']:
        return {'status': 'error', 'message': '暂不支持该分组字段'}

    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'success', 'group_by': group_by, 'grade': grade, 'records': []}

    result = []
    for group, sub in df.groupby(group_by):
        item = {
            'group': group,
            'count': int(len(sub)),
            'avg_mental_health': round(float(sub['dim_mental_health'].mean()), 2),
            'avg_academic_interest': round(float(sub['dim_academic_interest'].mean()), 2),
            'avg_research_engagement': round(float(sub['dim_research_engagement'].mean()), 2),
            'mentor_coverage_rate': round(float((sub['has_fixed_mentor'] > 0).mean() * 100), 2),
        }
        result.append(item)
    result.sort(key=lambda x: x['count'], reverse=True)
    return {'status': 'success', 'group_by': group_by, 'grade': grade, 'records': result}


@app.post('/api/formal/ai_chat')
async def formal_ai_chat(request: Request):
    df = load_df()
    if df.empty:
        return {'status': 'error', 'answer': '当前没有可用数据，暂时无法回答。'}

    body = await request.json()
    question = body.get('question', '').strip()
    page = body.get('page', 'overview')
    student_id = body.get('student_id')

    if not question:
        return {'status': 'error', 'answer': '请先输入问题。'}

    base_context = dataset_summary(df)
    student_text = ''
    if student_id is not None:
        sub = df[df['student_id'] == int(student_id)]
        if not sub.empty:
            student_text = student_context_text(sub.iloc[0])

    system_prompt = (
        '你是“相辉小助手”，服务于复旦大学相辉学堂人物画像系统。'
        '你已经了解当前学生模拟正式版数据结构与群体概况。'
        '回答要用中文，简洁、自然、可信，不要编造数据。'
        '如果用户问的是群体分析，就优先给整体发现、类型分布、风险提示和培养启发。'
        '如果用户问的是某个学生，就优先结合该生类型、维度、风险和建议路径来解释。'
        '对表现优异的学生：先肯定优势，建议不宜过多，更多给发展型、拓展型建议。'
        '对存在明显困难或短板的学生：先肯定已有努力和潜力，再给低门槛、可执行、可操作的建议，不要一味批评。'
        '避免用负面标签化语言，不要把学生写成“有问题的人”，而要写成“当前需要支持的人”。'
        '如果没有明显高风险，就不要硬凑风险。'
        '不要泄露 API key 或系统配置。'
    )
    user_prompt = f"页面：{page}\n群体背景：{base_context}\n"
    if student_text:
        user_prompt += f"当前学生信息：{student_text}\n"
    user_prompt += f"用户问题：{question}"

    ai_cfg = active_ai_config()
    if not ai_cfg['provider'] or not ai_cfg['api_key'] or not ai_cfg['model']:
        return {
            'status': 'success',
            'answer': f'【相辉小助手（离线说明）】我已经能读取这 200 名学生的群体概况与个人画像结构。你刚才的问题是：{question}。当前 AI 服务未配置成功，所以我先返回离线说明版回答。'
        }

    try:
        if ai_cfg['provider'] == 'anthropic':
            if not ai_cfg['base_url']:
                raise RuntimeError('AI_BASE_URL 未配置')
            answer = await ask_anthropic_compatible(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                base_url=ai_cfg['base_url'],
                api_key=ai_cfg['api_key'],
                model=ai_cfg['model'],
            )
        else:
            answer = await ask_openai_compatible(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=ai_cfg['model'],
            )
        return {'status': 'success', 'answer': answer}
    except Exception as e:
        return {'status': 'error', 'answer': f'相辉小助手调用失败：{e}'}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 新功能 1：导师画像
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.get('/api/formal/mentors')
def formal_mentors(grade: Optional[int] = Query(default=None)):
    """按学生类型分组，模拟导师视角的学生群体画像"""
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'success', 'records': []}

    records = []
    for stype, sub in df.groupby('student_type'):
        total = len(sub)
        dims = {k: round(float(sub[k].mean()), 2) for k in DIMENSION_LABELS}
        mentor_rate = round(float((sub['has_fixed_mentor'] > 0).mean() * 100), 1)
        wc = sub['warning_level'].value_counts().to_dict()
        records.append({
            'mentor_label': f'学术志趣组-{stype}',
            'student_type': stype,
            'total_students': total,
            'dimensions': dims,
            'mentor_coverage_rate': mentor_rate,
            'avg_type_confidence': round(float(sub['student_type_confidence'].mean()), 2),
            'research_rate': round(float((sub['research_participation_level'] >= 3).mean() * 100), 1),
            'avg_mental_health': round(float(sub['dim_mental_health'].mean()), 2),
            'overload_rate': round(float((sub['stress_level'] >= 4).mean() * 100), 1),
            'warning_distribution': {
                'red': int(wc.get('red', 0)),
                'yellow': int(wc.get('yellow', 0)),
                'green': int(wc.get('green', 0)),
                'none': int(wc.get('none', 0)),
            },
        })
    records.sort(key=lambda x: x['total_students'], reverse=True)
    return {'status': 'success', 'grade': grade, 'total_groups': len(records), 'records': records}


@app.get('/api/formal/mentors/{mentor_id}')
def formal_mentor_detail(mentor_id: str, grade: Optional[int] = Query(default=None)):
    """单个导师（学生类型组）的详细信息"""
    import urllib.parse
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    df = filter_df(df, grade=grade)
    decoded = urllib.parse.unquote(mentor_id)
    sub = df[df['student_type'] == decoded]
    if sub.empty:
        return {'status': 'error', 'message': '未找到该导师组'}
    wc = sub['warning_level'].value_counts().to_dict()
    students = []
    for _, row in sub.iterrows():
        students.append({
            'student_id': int(row['student_id']),
            'name': row['name'],
            'grade': int(row['grade']),
            'major_track': row['major_track'],
            'warning_level': row['warning_level'],
            'mental_health': round(float(row['dim_mental_health']), 2),
            'academic_interest': round(float(row['dim_academic_interest']), 2),
            'research_engagement': round(float(row['dim_research_engagement']), 2),
        })
    return {
        'status': 'success',
        'mentor_id': mentor_id,
        'student_type': decoded,
        'total_students': len(sub),
        'dimensions': {k: round(float(sub[k].mean()), 2) for k in DIMENSION_LABELS},
        'mentor_coverage_rate': round(float((sub['has_fixed_mentor'] > 0).mean() * 100), 1),
        'avg_type_confidence': round(float(sub['student_type_confidence'].mean()), 2),
        'warning_distribution': {
            'red': int(wc.get('red', 0)),
            'yellow': int(wc.get('yellow', 0)),
            'green': int(wc.get('green', 0)),
            'none': int(wc.get('none', 0)),
        },
        'students': students,
    }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 新功能 2：学生发展趋势
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.get('/api/formal/students/{student_id}/growth')
def formal_student_growth(student_id: int):
    """单个学生的时间发展曲线（模拟纵向数据）"""
    df = load_df()
    sub = df[df['student_id'] == student_id]
    if sub.empty:
        return {'status': 'error', 'message': '未找到该学生'}
    row = sub.iloc[0]
    growth = build_growth_series(row)
    return {
        'status': 'success',
        'student_id': student_id,
        'name': row['name'],
        'current_grade': int(row['grade']),
        'growth_series': growth,
        'current_dimensions': {
            '学术志趣': round(float(row['dim_academic_interest']), 2),
            '科研参与': round(float(row['dim_research_engagement']), 2),
            '心理健康': round(float(row['dim_mental_health']), 2),
            '导学关系': round(float(row['dim_mentorship']), 2),
        }
    }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 新功能 3：预警预测
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.get('/api/formal/prediction')
def formal_prediction(
    grade: Optional[int] = Query(default=None),
    risk_type: Optional[str] = Query(default=None),
    limit: int = Query(default=30, ge=1, le=200),
):
    """
    基于维度得分预测未来可能触发预警的学生。
    risk_type: mental / research / mentor / academic
    """
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'success', 'records': []}

    risk_defs = {
        'mental': {
            'condition': lambda r: r['dim_mental_health'] < 45 and r['stress_level'] >= 3,
            'score': lambda r: max(0, 45 - r['dim_mental_health']) + r['stress_level'] * 5,
            'label': '心理健康预警风险',
        },
        'research': {
            'condition': lambda r: r['dim_research_engagement'] < 40 and r['grade'] >= 2,
            'score': lambda r: max(0, 40 - r['dim_research_engagement']) + (r['grade'] - 1) * 5,
            'label': '科研参与不足风险',
        },
        'mentor': {
            'condition': lambda r: r['has_fixed_mentor'] == 0 and r['grade'] >= 2,
            'score': lambda r: 30 + (r['grade'] - 1) * 10,
            'label': '导师缺失风险',
        },
        'academic': {
            'condition': lambda r: r['stress_level'] >= 4 and r['dim_resilience'] < 55,
            'score': lambda r: (r['stress_level'] - 3) * 10 + max(0, 55 - r['dim_resilience']),
            'label': '学业压力超载风险',
        },
    }

    if risk_type and risk_type not in risk_defs:
        return {'status': 'error', 'message': '不支持的风险类型，可选: mental/research/mentor/academic'}

    seen = {}
    for _, row in df[df['warning_level'] != 'red'].iterrows():
        for rtype, rule in risk_defs.items():
            if risk_type and rtype != risk_type:
                continue
            if rule['condition'](row):
                score = float(rule['score'](row))
                if score < 10:
                    continue
                sid = int(row['student_id'])
                if sid not in seen or score > seen[sid][0]:
                    seen[sid] = (score, {
                        'student_id': sid,
                        'name': row['name'],
                        'grade': int(row['grade']),
                        'major_type': row['major_track'],
                        'risk_type': rtype,
                        'risk_label': rule['label'],
                        'risk_score': round(score, 1),
                        'mental_health': round(float(row['dim_mental_health']), 2),
                        'research_engagement': round(float(row['dim_research_engagement']), 2),
                        'stress_level': float(row['stress_level']),
                        'has_mentor': bool(row['has_fixed_mentor'] > 0),
                        'current_warning_level': row['warning_level'],
                    })

    records = [v[1] for v in sorted(seen.values(), key=lambda x: x[0], reverse=True)][:limit]
    return {'status': 'success', 'grade': grade, 'risk_type': risk_type, 'total_at_risk': len(records), 'records': records}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 新功能 4：对比分析
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.get('/api/formal/compare')
def formal_compare(
    student_ids: str = Query(default='', description='逗号分隔的学生ID'),
    group_by: Optional[str] = Query(default=None),
    grade: Optional[int] = Query(default=None),
):
    """
    自由选择多个学生（student_ids）或按群体字段（group_by）进行雷达图对比。
    group_by 可选: student_type / warning_level / admission_type / major_track
    """
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'success', 'groups': [], 'labels': []}

    groups, labels = [], []

    if student_ids:
        try:
            ids = [int(x.strip()) for x in student_ids.split(',') if x.strip()]
        except ValueError:
            return {'status': 'error', 'message': 'student_ids 格式应为逗号分隔的数字ID'}
        sub = df[df['student_id'].isin(ids)]
        if sub.empty:
            return {'status': 'error', 'message': '未找到匹配的学生'}
        for _, row in sub.iterrows():
            groups.append({
                'label': row['name'],
                'type': 'student',
                'student_id': int(row['student_id']),
                'dimensions': {k: round(float(row[k]), 2) for k in DIMENSION_LABELS},
                'mental_health': round(float(row['dim_mental_health']), 2),
                'research_engagement': round(float(row['dim_research_engagement']), 2),
                'warning_level': row['warning_level'],
                'student_type': row['student_type'],
            })
            labels.append(row['name'])

    if group_by:
        if group_by not in ['student_type', 'warning_level', 'admission_type', 'major_track']:
            return {'status': 'error', 'message': '暂不支持该分组字段'}
        for gval, sub in df.groupby(group_by):
            groups.append({
                'label': str(gval),
                'type': 'group',
                'count': int(len(sub)),
                'dimensions': {k: round(float(sub[k].mean()), 2) for k in DIMENSION_LABELS},
                'avg_mental_health': round(float(sub['dim_mental_health'].mean()), 2),
                'avg_research_engagement': round(float(sub['dim_research_engagement'].mean()), 2),
                'warning_distribution': sub['warning_level'].value_counts().to_dict(),
            })
            labels.append(f'{gval}({len(sub)}人)')

    if not groups:
        return {'status': 'error', 'message': '请提供 student_ids 或 group_by 参数'}

    return {'status': 'success', 'compare_type': 'students' if student_ids else 'groups',
            'dimension_labels': DIMENSION_LABELS, 'groups': groups, 'labels': labels}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 新功能 5：流失风险评估
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.get('/api/formal/churn_risk')
def formal_churn_risk(
    grade: Optional[int] = Query(default=None),
    threshold: float = Query(default=50.0, ge=0, le=100),
    limit: int = Query(default=50, ge=1, le=200),
):
    """
    流失风险评分 = 心理健康低(30%) + 科研参与低(20%) + 导师缺失(20%) + 压力过高(20%) + 类型信心不足(10%)
    """
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'success', 'records': []}

    records = []
    for _, row in df.iterrows():
        mental = max(0, 55 - row['dim_mental_health']) * 2
        research = max(0, 45 - row['dim_research_engagement']) * 1.5
        mentor = 40 if row['has_fixed_mentor'] == 0 else 0
        stress = (row['stress_level'] - 2) * 15 if row['stress_level'] >= 3 else 0
        confidence = max(0, 60 - row['student_type_confidence'] * 100) * 0.5
        total = min(100, round(mental * 0.3 + research * 0.2 + mentor * 0.2 + stress * 0.2 + confidence * 0.1, 1))
        if total < threshold:
            continue
        level = 'high' if total >= 70 else 'medium' if total >= 50 else 'low'
        records.append({
            'student_id': int(row['student_id']),
            'name': row['name'],
            'grade': int(row['grade']),
            'major_track': row['major_track'],
            'student_type': row['student_type'],
            'churn_risk_score': total,
            'risk_level': level,
            'risk_breakdown': {
                'mental_risk': round(mental, 1),
                'research_risk': round(research, 1),
                'mentor_risk': round(mentor, 1),
                'stress_risk': round(stress, 1),
                'confidence_risk': round(confidence, 1),
            },
            'current_warning_level': row['warning_level'],
            'mental_health': round(float(row['dim_mental_health']), 2),
            'has_mentor': bool(row['has_fixed_mentor'] > 0),
        })

    records.sort(key=lambda x: x['churn_risk_score'], reverse=True)
    return {'status': 'success', 'grade': grade, 'threshold': threshold,
            'total_at_risk': len(records), 'records': records[:limit]}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 新功能 6：班级视图
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.get('/api/formal/classes')
def formal_classes(grade: Optional[int] = Query(default=None)):
    """按年级+专业方向聚合的班级视图"""
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    df = filter_df(df, grade=grade)
    if df.empty:
        return {'status': 'success', 'records': []}

    records = []
    for (gr, track), sub in df.groupby(['grade', 'major_track']):
        wc = sub['warning_level'].value_counts().to_dict()
        records.append({
            'class_key': f'{gr}级-{track}',
            'grade': int(gr),
            'major_track': track,
            'total_students': int(len(sub)),
            'dimensions': {k: round(float(sub[k].mean()), 2) for k in DIMENSION_LABELS},
            'avg_mental_health': round(float(sub['dim_mental_health'].mean()), 2),
            'avg_research_engagement': round(float(sub['dim_research_engagement'].mean()), 2),
            'mentor_coverage_rate': round(float((sub['has_fixed_mentor'] > 0).mean() * 100), 1),
            'warning_distribution': {
                'red': int(wc.get('red', 0)),
                'yellow': int(wc.get('yellow', 0)),
                'green': int(wc.get('green', 0)),
                'none': int(wc.get('none', 0)),
            },
        })
    records.sort(key=lambda x: (x['grade'], x['major_track']))
    return {'status': 'success', 'grade': grade, 'total_classes': len(records), 'records': records}


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', '8002'))
    print(f'⚡ 正式版后端已启动: http://127.0.0.1:{port}')
    uvicorn.run(app, host='0.0.0.0', port=port)
