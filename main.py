import streamlit as st
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Radar, Pie
from streamlit_echarts import st_pyecharts
from datetime import datetime
import os
import json
import io


def load_data(file_path):
    # 如果目录不存在则创建
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 如果文件不存在则创建空文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([], f)
    return []


def save_data(data, file_path):
    # 如果目录不存在则创建
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def create_personnel_template():
    df = pd.DataFrame({
        "姓名": ["张三", "李四", "王五"],
        "电话": ["13800000001", "13800000002", "13800000003"],
        "学号": ["2023001", "2023002", "2023003"],
        "中队": ["一中队", "二中队", "三中队"]
    })
    return df


def create_evaluation_template():
    df = pd.DataFrame({
        "姓名": ["张三", "李四", "王五"],
        "学号": ["2023001", "2023002", "2023003"],
        "警容分数": [90, 85, 95],
        "风纪分数": [85, 90, 88],
        "表现分数": [95, 92, 87],
        "考核日期": ["2023-10-01", "2023-10-01", "2023-10-01"]
    })
    return df


def main():
    # 设置页面标题和配置
    st.set_page_config(
        page_title="警容风纪考核系统",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("警容风纪考核系统")

    # 创建侧边栏菜单
    menu = st.sidebar.selectbox(
        "功能选择",
        ["信息录入", "信息查询", "统计分析", "数据管理"]
    )

    # 信息录入页面
    if menu == "信息录入":
        st.header("信息录入")

        # 创建分页
        tab1, tab2, tab3 = st.tabs(["人员信息录入", "考核信息录入", "批量数据导入"])

        with tab1:
            st.subheader("人员信息录入")
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("姓名")
                phone = st.text_input("电话")

            with col2:
                student_id = st.text_input("学号")
                squad = st.text_input("中队")

            if st.button("提交人员信息"):
                if name and phone and student_id and squad:
                    # 准备人员信息数据
                    personnel_data = {
                        "姓名": name,
                        "电话": phone,
                        "学号": student_id,
                        "中队": squad
                    }

                    # 确保data目录存在
                    if not os.path.exists("data"):
                        os.makedirs("data")

                    # 读取现有数据或创建新列表
                    personnel_file = "data/personnel.json"
                    personnel_list = load_data(personnel_file)

                    # 添加新数据并保存
                    personnel_list.append(personnel_data)
                    save_data(personnel_list, personnel_file)

                    st.success("人员信息已保存")
                else:
                    st.warning("请填写所有信息")

        with tab2:
            st.subheader("考核信息录入")
            col1, col2 = st.columns(2)

            with col1:
                eval_name = st.text_input("姓名（考核）")
                eval_student_id = st.text_input("学号（考核）")
                appearance_score = st.number_input("警容分数", min_value=0, max_value=100)
                discipline_score = st.number_input("风纪分数", min_value=0, max_value=100)

            with col2:
                performance_score = st.number_input("表现分数", min_value=0, max_value=100)
                eval_date = st.date_input("考核日期")

            if st.button("提交考核信息"):
                if eval_name and eval_student_id:
                    # 准备考核信息数据
                    evaluation_data = {
                        "姓名": eval_name,
                        "学号": eval_student_id,
                        "警容分数": appearance_score,
                        "风纪分数": discipline_score,
                        "表现分数": performance_score,
                        "考核日期": str(eval_date)
                    }

                    # 确保data目录存在
                    if not os.path.exists("data"):
                        os.makedirs("data")

                    # 读取现有数据或创建新列表
                    evaluations_file = "data/evaluations.json"
                    evaluations_list = load_data(evaluations_file)

                    # 添加新数据并保存
                    evaluations_list.append(evaluation_data)
                    save_data(evaluations_list, evaluations_file)

                    # 创建柱状图
                    bar = Bar()
                    bar.add_xaxis(["警容分数", "风纪分数", "表现分数"])
                    bar.add_yaxis("得分", [appearance_score, discipline_score, performance_score])
                    bar.set_global_opts(title_opts=opts.TitleOpts(title="考核得分情况"))

                    # 创建饼图
                    pie = Pie()
                    pie.add(
                        "",
                        [
                            ["警容分数", appearance_score],
                            ["风纪分数", discipline_score],
                            ["表现分数", performance_score]
                        ]
                    )
                    pie.set_global_opts(title_opts=opts.TitleOpts(title="分数占比"))

                    # 保存图表
                    if not os.path.exists("charts"):
                        os.makedirs("charts")

                    # 显示图表
                    st.subheader("考核得分柱状图")
                    st_pyecharts(bar)

                    st.subheader("考核得分饼图")
                    st_pyecharts(pie)

                    st.success("考核信息已保存，图表已生成")
                else:
                    st.warning("请填写姓名和学号")

        with tab3:
            st.subheader("批量数据导入")

            # 模板下载
            st.markdown("### 下载数据模板")
            col1, col2 = st.columns(2)

            with col1:
                personnel_template = create_personnel_template()
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    personnel_template.to_excel(writer, sheet_name='Sheet1', index=False)
                st.download_button(
                    label="下载人员信息模板",
                    data=buffer.getvalue(),
                    file_name="personnel_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_personnel"
                )

            with col2:
                evaluation_template = create_evaluation_template()
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    evaluation_template.to_excel(writer, sheet_name='Sheet1', index=False)
                st.download_button(
                    label="下载考核信息模板",
                    data=buffer.getvalue(),
                    file_name="evaluation_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_evaluation"
                )

            # 文件上传
            st.markdown("### 上传数据文件")
            uploaded_file = st.file_uploader("选择Excel文件", type=['xlsx', 'xls'])

            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)
                    st.write("预览上传数据:")
                    st.dataframe(df)

                    # 根据表头自动识别数据类型
                    columns = set(df.columns)
                    personnel_columns = {"姓名", "电话", "学号", "中队"}
                    evaluation_columns = {"姓名", "学号", "警容分数", "风纪分数", "表现分数", "考核日期"}

                    if personnel_columns.issubset(columns):
                        data_type = "人员信息"
                    elif evaluation_columns.issubset(columns):
                        data_type = "考核信息"
                    else:
                        st.error("无法识别数据类型，请检查文件格式是否正确")
                        st.stop()

                    if st.button("确认导入"):
                        if data_type == "人员信息":
                            personnel_list = load_data("data/personnel.json")
                            new_data = df.to_dict('records')
                            personnel_list.extend(new_data)
                            save_data(personnel_list, "data/personnel.json")
                        else:
                            evaluations_list = load_data("data/evaluations.json")
                            new_data = df.to_dict('records')
                            evaluations_list.extend(new_data)
                            save_data(evaluations_list, "data/evaluations.json")

                        st.success(f"{data_type}已成功导入")
                except Exception as e:
                    st.error(f"导入失败: {str(e)}")

    # 信息查询页面
    elif menu == "信息查询":
        st.header("信息查询")

        # 加载人员数据
        personnel_list = load_data("data/personnel.json")
        evaluations_list = load_data("data/evaluations.json")

        if not personnel_list:
            st.warning("暂无人员数据")
            return

        # 获取所有人员的姓名和学号
        df_personnel = pd.DataFrame(personnel_list)
        all_names = df_personnel["姓名"].unique().tolist()
        all_ids = df_personnel["学号"].unique().tolist()

        search_type = st.radio("选择查询方式", ["按姓名查询", "按学号查询"])

        if search_type == "按姓名查询":
            search_name = st.selectbox("选择姓名", all_names)
            if st.button("查询"):
                person_data = [p for p in personnel_list if p["姓名"] == search_name]
                eval_data = [e for e in evaluations_list if e["姓名"] == search_name]

                if person_data:
                    st.subheader("人员信息")
                    st.dataframe(pd.DataFrame(person_data))
                if eval_data:
                    st.subheader("考核记录")
                    st.dataframe(pd.DataFrame(eval_data))

                if not person_data and not eval_data:
                    st.warning("未找到相关数据")

        else:  # 按学号查询
            search_id = st.selectbox("选择学号", all_ids)
            if st.button("查询"):
                person_data = [p for p in personnel_list if p["学号"] == search_id]
                eval_data = [e for e in evaluations_list if e["学号"] == search_id]

                if person_data:
                    st.subheader("人员信息")
                    st.dataframe(pd.DataFrame(person_data))
                if eval_data:
                    st.subheader("考核记录")
                    st.dataframe(pd.DataFrame(eval_data))

                if not person_data and not eval_data:
                    st.warning("未找到相关数据")

    # 统计分析页面
    elif menu == "统计分析":
        st.header("统计分析")
        evaluations_list = load_data("data/evaluations.json")
        if evaluations_list:
            df = pd.DataFrame(evaluations_list)

            st.subheader("总体统计")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("平均警容分数", f"{df['警容分数'].mean():.2f}")
            with col2:
                st.metric("平均风纪分数", f"{df['风纪分数'].mean():.2f}")
            with col3:
                st.metric("平均表现分数", f"{df['表现分数'].mean():.2f}")

            st.subheader("成绩分布")
            # 柱状图
            bar = Bar()
            bar.add_xaxis(["警容分数", "风纪分数", "表现分数"])
            bar.add_yaxis("平均分", [
                round(df['警容分数'].mean(), 2),
                round(df['风纪分数'].mean(), 2),
                round(df['表现分数'].mean(), 2)
            ])
            bar.set_global_opts(title_opts=opts.TitleOpts(title="各项平均分"))
            st_pyecharts(bar)

            # 饼图
            total_scores = (
                    df['警容分数'].mean() +
                    df['风纪分数'].mean() +
                    df['表现分数'].mean()
            )
            pie = Pie()
            pie.add(
                "",
                [
                    ["警容分数", round(df['警容分数'].mean(), 2)],
                    ["风纪分数", round(df['风纪分数'].mean(), 2)],
                    ["表现分数", round(df['表现分数'].mean(), 2)]
                ]
            )
            pie.set_global_opts(title_opts=opts.TitleOpts(title="平均分数占比"))
            st_pyecharts(pie)
        else:
            st.info("暂无考核数据")

    # 数据管理页面
    elif menu == "数据管理":
        st.header("数据管理")

        data_type = st.radio("选择数据类型", ["人员信息", "考核信息"])

        if data_type == "人员信息":
            personnel_list = load_data("data/personnel.json")
            if personnel_list:
                df = pd.DataFrame(personnel_list)
                edited_df = st.data_editor(df)

                if st.button("保存修改"):
                    updated_data = edited_df.to_dict('records')
                    save_data(updated_data, "data/personnel.json")
                    st.success("修改已保存")
            else:
                st.info("暂无人员数据")

        else:  # 考核信息
            evaluations_list = load_data("data/evaluations.json")
            if evaluations_list:
                df = pd.DataFrame(evaluations_list)
                edited_df = st.data_editor(df)

                if st.button("保存修改"):
                    updated_data = edited_df.to_dict('records')
                    save_data(updated_data, "data/evaluations.json")
                    st.success("修改已保存")
            else:
                st.info("暂无考核数据")


if __name__ == '__main__':
    main()
