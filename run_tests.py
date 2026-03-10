"""
运行所有单元测试
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """
    运行所有单元测试
    
    Returns:
        int: 测试退出码（0表示成功，非0表示失败）
    """
    print("=" * 60)
    print("开始运行单元测试...")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=False
        )
        
        print()
        print("=" * 60)
        if result.returncode == 0:
            print("✓ 所有测试通过！")
        else:
            print("✗ 部分测试失败")
        print("=" * 60)
        
        return result.returncode
    except Exception as e:
        print(f"运行测试时出错: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
