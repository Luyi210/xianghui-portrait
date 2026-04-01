import math
import random
from typing import Dict, List

import numpy as np
import pandas as pd

np.random.seed(20260311)
random.seed(20260311)

PROVINCES = [
    '北京', '上海', '天津', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
    '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
    '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
    '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门'
]

MAJORS = ['物理', '数学', '化学', '生物', '计算机']
ADMISSION_TYPES = ['强基', '统招', '竞赛', '综评']
REGION_TYPES = ['农村', '县城', '地级市', '省会城市', '直辖市']
HIGH_SCHOOL_LEVELS = ['顶尖', '强省重点', '普通重点', '一般']
GENDERS = ['男', '女']
TYPES = ['科研驱动型', '竞赛转型型', '均衡发展型', '压力应对型', '探索迷茫型']


def clip100(value: float) -> float:
    return round(float(np.clip(value, 0, 100)), 2)


def likert(mu: float, sigma: float = 12) -> float:
    return clip100(np.random.normal(mu, sigma))


def bernoulli(prob: float) -> int:
    return int(np.random.random() < prob)


def scaled_count(max_count: int, lam: float) -> (int, float):
    count = min(np.random.poisson(lam), max_count)
    score = clip100(count / max_count * 100)
    return int(count), score


def compute_dimensions(row: Dict) -> Dict[str, float]:
    dims = {}
    dims['dim_academic_interest'] = clip100(
        0.22 * row['academic_identity']
        + 0.20 * row['scientist_aspiration']
        + 0.18 * row['major_understanding']
        + 0.18 * row['goal_clarity']
        + 0.12 * row['learning_passion']
        + 0.10 * row['interdisciplinary_willingness']
    )
    dims['dim_resilience'] = clip100(
        0.30 * row['resilience_level']
        + 0.22 * row['critical_thinking']
        + 0.24 * row['self_discipline']
        + 0.14 * row['learning_passion']
        + 0.10 * (100 - row['stress_level'])
    )
    dims['dim_innovation'] = clip100(
        0.28 * row['curiosity_score']
        + 0.20 * row['risk_taking_score']
        + 0.10 * row['impulsiveness_score']
        + 0.22 * row['interdisciplinary_association']
        + 0.12 * row['interdisciplinary_willingness']
        + 0.08 * row['ai_use_creative']
    )
    dims['dim_learning_motivation'] = clip100(
        0.24 * row['motivation_strength']
        + 0.24 * row['motivation_intrinsic']
        + 0.20 * row['motivation_mission']
        + 0.14 * row['goal_clarity']
        + 0.12 * row['learning_passion']
        + 0.06 * (100 - row['motivation_external'])
    )
    dims['dim_research_engagement'] = clip100(
        0.20 * row['research_participation_level']
        + 0.16 * row['research_project_score']
        + 0.14 * row['research_platform_level']
        + 0.22 * row['research_depth_score']
        + 0.10 * row['fdurop_participated']
        + 0.10 * row['fdurop_gain_score']
        + 0.08 * row['mentor_guidance_frequency']
    )
    dims['dim_mentorship'] = clip100(
        0.16 * row['has_fixed_mentor']
        + 0.22 * row['mentor_closeness']
        + 0.22 * row['mentor_inspiration']
        + 0.16 * row['mentor_guidance_frequency']
        + 0.12 * row['personalized_support']
        + 0.06 * row['peer_support_score']
        + 0.06 * row['peer_academic_interaction']
    )
    dims['dim_environment_satisfaction'] = clip100(
        0.10 * row['facility_satisfaction']
        + 0.08 * row['frontier_exposure']
        + 0.06 * row['international_exposure']
        + 0.12 * row['policy_flexibility']
        + 0.12 * row['evaluation_fairness']
        + 0.12 * row['innovation_climate']
        + 0.10 * row['personalized_support']
        + 0.08 * row['cross_college_exchange']
        + 0.14 * row['overall_env_satisfaction']
        + 0.04 * row['pnp_helpfulness']
        + 0.04 * row['aplus_incentive_score']
    )
    dims['dim_mental_health'] = clip100(
        0.42 * row['mental_health_score']
        + 0.18 * (100 - row['stress_level'])
        + 0.14 * row['peer_support_score']
        + 0.12 * row['mentor_closeness']
        + 0.14 * (100 - row['workload_feeling'])
    )
    return dims


def classify_student(row: pd.Series) -> Dict[str, object]:
    dims = [
        row['dim_academic_interest'], row['dim_resilience'], row['dim_innovation'],
        row['dim_learning_motivation'], row['dim_research_engagement'], row['dim_mentorship'],
        row['dim_environment_satisfaction'], row['dim_mental_health']
    ]
    matches: List[tuple] = []

    if row['dim_resilience'] >= 60 and row['dim_mental_health'] <= 45 and row['stress_level'] >= 70:
        conf = min(98, 60 + (row['stress_level'] - 70) * 0.8 + (45 - row['dim_mental_health']) * 0.7)
        matches.append(('压力应对型', round(conf, 1)))
    if row['dim_research_engagement'] >= 75 and row['dim_academic_interest'] >= 70 and row['dim_mentorship'] >= 60:
        conf = min(98, 65 + (row['dim_research_engagement'] - 75) * 0.8 + (row['dim_academic_interest'] - 70) * 0.5)
        matches.append(('科研驱动型', round(conf, 1)))
    if row['dim_academic_interest'] <= 45 and row['goal_clarity'] <= 45 and row['dim_research_engagement'] <= 50:
        conf = min(98, 62 + (45 - row['dim_academic_interest']) * 0.7 + (45 - row['goal_clarity']) * 0.5)
        matches.append(('探索迷茫型', round(conf, 1)))
    if row['science_competition_level'] >= 70 and row['dim_innovation'] >= 65 and row['dim_academic_interest'] >= 55 and 40 <= row['dim_research_engagement'] <= 75:
        conf = min(98, 60 + (row['science_competition_level'] - 70) * 0.5 + (row['dim_innovation'] - 65) * 0.6)
        matches.append(('竞赛转型型', round(conf, 1)))
    if min(dims) >= 45 and np.std(dims) <= 12 and sum(v >= 60 for v in dims) >= 4:
        conf = min(95, 58 + (12 - np.std(dims)) * 2.2 + sum(v >= 60 for v in dims) * 2)
        matches.append(('均衡发展型', round(conf, 1)))

    priority = {'压力应对型': 5, '科研驱动型': 4, '探索迷茫型': 3, '竞赛转型型': 2, '均衡发展型': 1}
    if not matches:
        scores = {
            '科研驱动型': row['dim_research_engagement'] * 0.45 + row['dim_academic_interest'] * 0.35 + row['dim_mentorship'] * 0.20,
            '竞赛转型型': row['science_competition_level'] * 0.35 + row['dim_innovation'] * 0.35 + row['dim_academic_interest'] * 0.15 + (100 - abs(row['dim_research_engagement'] - 58)) * 0.15,
            '均衡发展型': (100 - np.std(dims) * 3) * 0.45 + np.mean(dims) * 0.55,
            '压力应对型': row['dim_resilience'] * 0.30 + row['stress_level'] * 0.35 + (100 - row['dim_mental_health']) * 0.35,
            '探索迷茫型': (100 - row['dim_academic_interest']) * 0.40 + (100 - row['goal_clarity']) * 0.30 + (100 - row['dim_research_engagement']) * 0.30,
        }
        ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        student_type, best_score = ordered[0]
        adjacent_type = ordered[1][0]
        confidence = round(min(88, 45 + abs(best_score - ordered[1][1]) * 0.8), 1)
        return {'student_type': student_type, 'student_type_confidence': confidence, 'adjacent_type': adjacent_type}

    matches = sorted(matches, key=lambda x: (priority[x[0]], x[1]), reverse=True)
    student_type = matches[0][0]
    confidence = matches[0][1]
    adjacent_type = matches[1][0] if len(matches) > 1 else '均衡发展型' if student_type != '均衡发展型' else '科研驱动型'
    return {'student_type': student_type, 'student_type_confidence': confidence, 'adjacent_type': adjacent_type}


def evaluate_risks(row: pd.Series) -> Dict[str, object]:
    severity = {}

    psych_red = row['mental_health_score'] <= 40 or row['pct_dim_mental_health'] <= 15 or (row['mental_health_score'] <= 50 and row['stress_level'] >= 80 and row['workload_feeling'] >= 80)
    psych_yellow = row['pct_dim_mental_health'] <= 25 or row['stress_level'] >= 75 or (row['workload_feeling'] >= 80 and row['peer_support_score'] < 50)
    psych_green = row['pct_dim_mental_health'] <= 35 or row['stress_level'] >= 65
    severity['risk_psychology'] = 'red' if psych_red else 'yellow' if psych_yellow else 'green' if psych_green else 'none'

    mentor_yellow = row['has_fixed_mentor'] == 0 and row['grade'] >= 2
    mentor_red = mentor_yellow and (row['grade'] >= 3 or row['dim_research_engagement'] < 45 or row['pct_dim_mentorship'] <= 15)
    severity['risk_no_mentor'] = 'red' if mentor_red else 'yellow' if mentor_yellow else 'none'

    interest_yellow = row['pct_dim_academic_interest'] <= 25 or row['goal_clarity'] <= 40
    interest_red = row['pct_dim_academic_interest'] <= 15 and row['motivation_external'] >= 75 and row['motivation_intrinsic'] <= 45
    severity['risk_low_interest'] = 'red' if interest_red else 'yellow' if interest_yellow else 'none'

    research_yellow = row['pct_dim_research_engagement'] <= 25 or row['research_participation_level'] <= 40 or row['research_depth_score'] <= 40
    research_red = row['grade'] >= 2 and row['research_participation_level'] <= 20 and row['has_fixed_mentor'] == 0
    severity['risk_low_research'] = 'red' if research_red else 'yellow' if research_yellow else 'none'

    ext_yellow = row['motivation_external'] >= 70 and row['motivation_intrinsic'] < 55
    ext_red = row['motivation_external'] >= 80 and row['motivation_intrinsic'] <= 40 and row['pct_dim_academic_interest'] <= 25
    severity['risk_external_driven'] = 'red' if ext_red else 'yellow' if ext_yellow else 'none'

    ai_green = row['ai_use_frequency'] <= 20 or (row['ai_use_learning'] <= 20 and row['ai_use_research'] <= 20 and row['ai_use_creative'] <= 20)
    ai_yellow = row['grade'] >= 2 and row['ai_use_frequency'] <= 20 and row['dim_learning_motivation'] < 60
    severity['risk_low_ai_usage'] = 'yellow' if ai_yellow else 'green' if ai_green else 'none'

    load_yellow = row['workload_feeling'] >= 80 or (row['stress_level'] >= 75 and row['self_discipline'] >= 70 and row['mental_health_score'] < 60)
    load_red = row['workload_feeling'] >= 85 and row['stress_level'] >= 80 and row['pct_dim_mental_health'] <= 25
    severity['risk_overload'] = 'red' if load_red else 'yellow' if load_yellow else 'none'

    red_count = sum(v == 'red' for v in severity.values())
    yellow_or_above = sum(v in ('red', 'yellow') for v in severity.values())
    green_or_above = sum(v != 'none' for v in severity.values())
    low15 = sum(row[c] <= 15 for c in [
        'pct_dim_academic_interest', 'pct_dim_resilience', 'pct_dim_innovation', 'pct_dim_learning_motivation',
        'pct_dim_research_engagement', 'pct_dim_mentorship', 'pct_dim_environment_satisfaction', 'pct_dim_mental_health'
    ])
    low25 = sum(row[c] <= 25 for c in [
        'pct_dim_academic_interest', 'pct_dim_resilience', 'pct_dim_innovation', 'pct_dim_learning_motivation',
        'pct_dim_research_engagement', 'pct_dim_mentorship', 'pct_dim_environment_satisfaction', 'pct_dim_mental_health'
    ])

    if severity['risk_psychology'] == 'red' or red_count >= 2 or (row['pct_dim_mental_health'] <= 15 and row['pct_dim_academic_interest'] <= 15) or low15 >= 3:
        warning_level = 'red'
    elif yellow_or_above >= 2 or low25 >= 2 or (row['student_type'] == '压力应对型' and row['pct_dim_mental_health'] <= 25) or (row['student_type'] == '探索迷茫型' and row['has_fixed_mentor'] == 0):
        warning_level = 'yellow'
    elif low25 >= 1 or green_or_above >= 1 or row['student_type'] == '探索迷茫型':
        warning_level = 'green'
    else:
        warning_level = 'none'

    flags = {k: int(v != 'none') for k, v in severity.items()}
    flags['warning_count'] = sum(flags.values())
    flags['warning_level'] = warning_level
    flags.update({f'{k}_severity': v for k, v in severity.items()})
    return flags


def build_issue_summary(row: pd.Series) -> str:
    messages = []
    mapping = {
        'risk_psychology': '心理健康与压力状态需要优先关注',
        'risk_no_mentor': '尚未建立稳定导师支持关系',
        'risk_low_interest': '学术志趣与目标清晰度偏弱',
        'risk_low_research': '科研参与深度不足',
        'risk_external_driven': '学习动力偏外部驱动',
        'risk_low_ai_usage': 'AI 学习工具利用不足',
        'risk_overload': '学业负担感偏高'
    }
    for key, text in mapping.items():
        if row.get(key, 0) == 1:
            messages.append(text)
    return '；'.join(messages[:4]) if messages else '当前整体状态稳定，可继续保持。'


def generate_advice_path(row: pd.Series) -> Dict[str, str]:
    academic, psychology, skill, resource = [], [], [], []

    if row['risk_low_interest']:
        academic.append('建议优先通过低风险试错课程、跨学科讲座和导师交流来重新确认兴趣方向。')
    if row['risk_low_research']:
        academic.append('建议从课程项目、FDUROP 或课题组旁听切入，逐步提升科研参与深度。')
    if row['risk_psychology'] or row['risk_overload']:
        psychology.append('建议近期优先处理压力管理问题，必要时寻求专业心理支持，并重新梳理学习节奏。')
    if row['risk_low_ai_usage']:
        skill.append('建议先从翻译、总结、检索、思路整理等低门槛场景开始使用 AI，再逐步扩展到科研与写作支持。')
    if row['student_type'] == '竞赛转型型':
        skill.append('建议把竞赛式能力迁移到研究问题定义、过程记录和阶段复盘中。')
    if row['risk_no_mentor']:
        resource.append('建议优先连接导师资源，并通过课程项目、FDUROP 和学术活动建立稳定指导关系。')
    if row['pnp_used'] == 0 and (row['risk_overload'] or row['risk_low_interest']):
        resource.append('建议结合当前课程负担，评估 P/NP 制度的合理使用空间，为探索和恢复留出余量。')

    path_templates = {
        '探索迷茫型': '先明确兴趣盲区，再参加跨学科活动并与导师/高年级同学交流，利用 P/NP 和低成本项目试探方向。',
        '压力应对型': '先减压与稳节奏，调整课程负担并使用制度工具降低焦虑，再逐步恢复长期学术目标。',
        '科研驱动型': '继续提升科研深度，对接更高平台与导师资源，同时加强成果表达与长期研究方向积累。',
        '竞赛转型型': '从解题导向转向问题导向，尽快进入真实研究场景，建立过程记录与学术表达习惯。',
        '均衡发展型': '保持稳定节奏，在优势维度上继续拉高，尝试承担更高挑战任务并形成个人特色。',
    }

    return {
        'advice_academic': ' '.join(academic) if academic else '建议保持当前学术节奏，并在已有优势维度上继续深化。',
        'advice_psychology': ' '.join(psychology) if psychology else '当前心理状态整体稳定，建议继续保持规律节奏与支持连接。',
        'advice_skill': ' '.join(skill) if skill else '建议继续提升学习工具与研究方法的使用效率。',
        'advice_resource': ' '.join(resource) if resource else '建议持续关注学堂资源、导师机会与跨学科平台。',
        'advice_path': path_templates.get(row['student_type'], path_templates['均衡发展型'])
    }


def percentile_series(series: pd.Series) -> pd.Series:
    return (series.rank(method='average', pct=True) * 100).round(2)


def make_student(i: int) -> Dict[str, object]:
    student_id = 20240001 + i
    grade = int(np.random.choice([1, 2, 3, 4], p=[0.32, 0.28, 0.22, 0.18]))
    major = random.choice(MAJORS)
    admission = np.random.choice(ADMISSION_TYPES, p=[0.28, 0.33, 0.17, 0.22])
    province = random.choice(PROVINCES)
    region_type = np.random.choice(REGION_TYPES, p=[0.12, 0.18, 0.28, 0.25, 0.17])
    hs_level = np.random.choice(HIGH_SCHOOL_LEVELS, p=[0.18, 0.35, 0.31, 0.16])

    competition_base = 78 if admission == '竞赛' else 52
    motivation_external_base = 70 if grade in [1, 2] else 58
    research_base = 28 + grade * 12
    mentor_prob = 0.42 + grade * 0.10

    project_count, project_score = scaled_count(4, 0.4 + grade * 0.6)

    row = {
        'student_id': student_id,
        'name': f'学生-{i + 1:03d}',
        'gender': random.choice(GENDERS),
        'birth_year': int(np.random.choice([2003, 2004, 2005, 2006])),
        'grade': grade,
        'major_track': major,
        'admission_type': admission,
        'source_province': province,
        'source_region_type': region_type,
        'high_school_level': hs_level,
        'gaokao_score': int(np.random.normal(664, 18)),
        'gaokao_rank_band': np.random.choice(['前1‰', '前5‰', '前1%', '前3%'], p=[0.14, 0.31, 0.33, 0.22]),
        'family_class_score': int(np.clip(round(np.random.normal(6.1, 1.7)), 1, 10)),
        'father_education': np.random.choice(['高中及以下', '大专', '本科', '硕士', '博士'], p=[0.17, 0.16, 0.33, 0.22, 0.12]),
        'mother_education': np.random.choice(['高中及以下', '大专', '本科', '硕士', '博士'], p=[0.19, 0.18, 0.35, 0.19, 0.09]),
        'father_occupation': np.random.choice(['教师/科研', '企业职员', '公务员/事业单位', '个体经营', '工人/服务业']),
        'mother_occupation': np.random.choice(['教师/科研', '企业职员', '公务员/事业单位', '个体经营', '工人/服务业']),
        'precollege_science_interest': likert(72),
        'precollege_self_learning': likert(68),
        'precollege_interdisciplinary': likert(63),
        'precollege_art_strength': likert(51),
        'science_competition_level': likert(competition_base, 20),
        'innovation_competition_role': likert(58),
        'overseas_exposure': bernoulli(0.16) * 100,
        'tutoring_years': int(np.clip(round(np.random.normal(3.5, 2.0)), 0, 10)),
        'tutoring_intensity': likert(54),
        'family_burden_feeling': likert(42),
        'academic_identity': likert(66),
        'scientist_aspiration': likert(62),
        'major_understanding': likert(58 + grade * 5),
        'goal_clarity': likert(54 + grade * 4),
        'resilience_level': likert(68),
        'critical_thinking': likert(64),
        'learning_passion': likert(67),
        'self_discipline': likert(69),
        'interdisciplinary_willingness': likert(65),
        'motivation_strength': likert(72),
        'motivation_intrinsic': likert(63),
        'motivation_external': likert(motivation_external_base, 18),
        'motivation_mission': likert(59),
        'mental_health_score': likert(63),
        'stress_level': likert(61 + grade * 4, 16),
        'curiosity_score': likert(72),
        'risk_taking_score': likert(58),
        'impulsiveness_score': likert(48),
        'interdisciplinary_association': likert(66),
        'ai_use_frequency': likert(52 + grade * 5),
        'ai_use_learning': likert(57 + grade * 5),
        'ai_use_research': likert(38 + grade * 8),
        'ai_use_coding': likert(25 if major != '计算机' else 62),
        'ai_use_creative': likert(47),
        'has_fixed_mentor': bernoulli(min(mentor_prob, 0.88)) * 100,
        'mentor_closeness': likert(45 + grade * 6),
        'mentor_inspiration': likert(48 + grade * 6),
        'mentor_guidance_frequency': likert(42 + grade * 8),
        'peer_support_score': likert(67),
        'peer_academic_interaction': likert(62),
        'facility_satisfaction': likert(69),
        'frontier_exposure': likert(63),
        'international_exposure': likert(49),
        'policy_flexibility': likert(61),
        'evaluation_fairness': likert(58),
        'innovation_climate': likert(67),
        'personalized_support': likert(55),
        'workload_feeling': likert(58 + grade * 4),
        'cross_college_exchange': likert(56),
        'overall_env_satisfaction': likert(64),
        'research_participation_level': likert(research_base, 20),
        'research_project_count': project_count,
        'research_project_score': project_score,
        'research_entry_path': np.random.choice(['导师', 'FDUROP', '任课教师', '竞赛延伸', '尚未进入'], p=[0.26, 0.18, 0.22, 0.14, 0.20]),
        'research_platform_level': likert(35 + grade * 10, 20),
        'research_depth_score': likert(30 + grade * 12, 19),
        'fdurop_participated': bernoulli(0.10 + grade * 0.12) * 100,
        'fdurop_gain_score': likert(44 + grade * 7),
        'pnp_used': bernoulli(0.18 + grade * 0.10) * 100,
        'pnp_helpfulness': likert(55),
        'aplus_received': bernoulli(0.12 + grade * 0.04) * 100,
        'aplus_incentive_score': likert(52),
        'integrated_training_identity': likert(63),
    }

    if admission == '竞赛':
        row['curiosity_score'] = clip100(row['curiosity_score'] + 6)
        row['science_competition_level'] = clip100(row['science_competition_level'] + 12)
        row['risk_taking_score'] = clip100(row['risk_taking_score'] + 8)
    if grade >= 3:
        row['major_understanding'] = clip100(row['major_understanding'] + 6)
        row['goal_clarity'] = clip100(row['goal_clarity'] + 5)
        row['research_depth_score'] = clip100(row['research_depth_score'] + 8)
    if row['has_fixed_mentor'] == 0:
        row['mentor_closeness'] = clip100(row['mentor_closeness'] - 18)
        row['mentor_inspiration'] = clip100(row['mentor_inspiration'] - 16)
        row['mentor_guidance_frequency'] = clip100(row['mentor_guidance_frequency'] - 20)
        row['personalized_support'] = clip100(row['personalized_support'] - 10)
    if row['stress_level'] > 78:
        row['mental_health_score'] = clip100(row['mental_health_score'] - random.uniform(8, 20))
    if row['research_participation_level'] > 72:
        row['fdurop_gain_score'] = clip100(row['fdurop_gain_score'] + 8)

    return row


def main(num_students: int = 220):
    rows = [make_student(i) for i in range(num_students)]
    df = pd.DataFrame(rows)

    dim_df = df.apply(lambda row: pd.Series(compute_dimensions(row)), axis=1)
    df = pd.concat([df, dim_df], axis=1)

    for col in [
        'dim_academic_interest', 'dim_resilience', 'dim_innovation', 'dim_learning_motivation',
        'dim_research_engagement', 'dim_mentorship', 'dim_environment_satisfaction', 'dim_mental_health'
    ]:
        df[f'z_{col}'] = ((df[col] - df[col].mean()) / df[col].std(ddof=0)).round(4)
        df[f'pct_{col}'] = percentile_series(df[col])

    type_df = df.apply(lambda row: pd.Series(classify_student(row)), axis=1)
    df = pd.concat([df, type_df], axis=1)

    risk_df = df.apply(lambda row: pd.Series(evaluate_risks(row)), axis=1)
    df = pd.concat([df, risk_df], axis=1)

    df['issue_summary'] = df.apply(build_issue_summary, axis=1)
    advice_df = df.apply(lambda row: pd.Series(generate_advice_path(row)), axis=1)
    df = pd.concat([df, advice_df], axis=1)

    type_features = {
        '科研驱动型': '学术方向较清晰，科研投入深，适合纵向培养与高水平平台对接。',
        '竞赛转型型': '前期能力基础较强，正在从竞赛型学习向研究型学习转变。',
        '均衡发展型': '整体发展稳定，没有明显短板，适合个性化拔高支持。',
        '压力应对型': '仍在努力应对学业挑战，但心理空间明显受压。',
        '探索迷茫型': '方向感不足，需要低成本试错、导师支持和资源引导。',
    }
    df['type_features'] = df['student_type'].map(type_features)
    df['benchmark_case'] = df['student_type'].map({
        '科研驱动型': '对标高年级科研持续投入、逐步形成稳定研究方向的学生路径。',
        '竞赛转型型': '对标从竞赛优势迁移到研究表达和问题定义的转型案例。',
        '均衡发展型': '对标在稳定基础上持续拉高优势维度的综合发展路径。',
        '压力应对型': '对标先稳节奏再恢复长期目标的减压转型路径。',
        '探索迷茫型': '对标通过导师连接和跨学科试探逐步澄清方向的学生路径。',
    })

    output = 'formal_student_data.csv'
    df.to_csv(output, index=False, encoding='utf-8-sig')
    print(f'✅ 正式版模拟数据已生成：{output}，共 {len(df)} 条')
    print('学生类型分布：')
    print(df['student_type'].value_counts().to_string())
    print('\n预警等级分布：')
    print(df['warning_level'].value_counts().to_string())


if __name__ == '__main__':
    main()
