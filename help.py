







class TaskManager:
    def __init__(self, condition_one=True, condition_two=False):
        # 条件，实例化时传入
        self.condition_one = condition_one
        self.condition_two = condition_two
        self.tasks = {}  # 定义任务字典

        # 自动注册任务
        self._register_tasks()

    def _register_tasks(self):
        """扫描当前实例的方法，根据条件注册任务"""
        for attr_name in dir(self):  # 遍历实例的属性和方法
            attr = getattr(self, attr_name)
            # 找出被标记为任务的函数
            if callable(attr) and hasattr(attr, "_task_key"):
                # 获取任务键名和条件
                task_key = attr._task_key
                condition_name = attr._condition_name
                # 只有满足条件时将函数添加到任务字典
                if getattr(self, condition_name, False):
                    self.tasks[task_key] = attr

    @staticmethod
    def conditional_task(task_key, condition_name):
        """
        装饰器：为函数标记任务键和条件
        - task_key: 任务的唯一标识（键名）
        - condition_name: 类或实例中作为条件的属性名
        """

        def decorator(func):
            # 标记任务键名和条件
            func._task_key = task_key
            func._condition_name = condition_name
            return func

        return decorator

    @conditional_task("task_one", "condition_one")
    def task_one(self):
        print("执行任务一！")

    @conditional_task("task_two", "condition_two")
    def task_two(self):
        print("执行任务二！")

    def run_task(self, task_key):
        """运行指定键对应的任务"""
        if task_key in self.tasks:
            self.tasks[task_key]()
        else:
            print(f"任务 {task_key} 不存在或未注册！")

    def run_all_tasks(self):
        """统一执行字典中所有任务"""
        print("执行任务字典中的函数：")
        for key, task in self.tasks.items():
            print(f"执行任务：{key}")
            task()


# 测试用例 1
print("实例 1 测试：")
manager1 = TaskManager(condition_one=True, condition_two=False)
manager1.run_all_tasks()  # 执行任务字典中的所有任务


# 测试用例 2
print("\n实例 2 测试：")
manager2 = TaskManager(condition_one=False, condition_two=True)
manager2.run_all_tasks()  # 执行任务字典中的所有任务



