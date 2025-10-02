#!/usr/bin/env python3
"""
랜덤 테스트 데이터 생성기
C++ 정렬 알고리즘 테스트를 위한 다양한 패턴의 랜덤 데이터를 생성합니다.
"""

import random
import argparse
import sys
from enum import Enum
from typing import List

class DataPattern(Enum):
    """데이터 패턴 종류"""
    RANDOM = "random"           # 완전 랜덤
    SORTED = "sorted"          # 오름차순 정렬됨
    REVERSE = "reverse"        # 내림차순 정렬됨
    PARTIAL_SORTED = "partial" # 부분적으로 정렬됨
    DUPLICATES = "duplicates"  # 중복값 많음
    NEARLY_SORTED = "nearly"   # 거의 정렬됨 (몇 개만 위치 바뀜)

class TestDataGenerator:
    """테스트 데이터 생성 클래스"""
    
    def __init__(self, seed=None):
        """
        생성자
        Args:
            seed: 랜덤 시드 (None이면 현재 시간 기반)
        """
        if seed is not None:
            random.seed(seed)
            self.seed = seed
        else:
            self.seed = random.randint(0, 2**32 - 1)
            random.seed(self.seed)
    
    def generate_random_data(self, size: int, min_val: int = -1000000, max_val: int = 1000000) -> List[int]:
        """완전 랜덤 데이터 생성"""
        return [random.randint(min_val, max_val) for _ in range(size)]
    
    def generate_sorted_data(self, size: int, min_val: int = 1, max_val: int = 1000000) -> List[int]:
        """오름차순 정렬된 데이터 생성"""
        data = []
        current = min_val
        step_range = max(1, (max_val - min_val) // size)
        
        for _ in range(size):
            data.append(current)
            current += random.randint(0, step_range * 2)
            if current > max_val:
                current = max_val
        
        return data
    
    def generate_reverse_data(self, size: int, min_val: int = 1, max_val: int = 1000000) -> List[int]:
        """내림차순 정렬된 데이터 생성"""
        return sorted(self.generate_random_data(size, min_val, max_val), reverse=True)
    
    def generate_partial_sorted_data(self, size: int, min_val: int = -1000000, max_val: int = 1000000) -> List[int]:
        """부분적으로 정렬된 데이터 생성 (70% 정렬, 30% 랜덤)"""
        sorted_size = int(size * 0.7)
        random_size = size - sorted_size
        
        # 정렬된 부분 생성
        sorted_part = self.generate_sorted_data(sorted_size, min_val, max_val // 2)
        
        # 랜덤 부분 생성
        random_part = self.generate_random_data(random_size, max_val // 2, max_val)
        
        # 두 부분을 합치고 섞기
        data = sorted_part + random_part
        
        # 일부만 섞어서 부분적으로 정렬된 상태 만들기
        shuffle_count = size // 10  # 10% 정도만 위치 바꾸기
        for _ in range(shuffle_count):
            i, j = random.randint(0, size-1), random.randint(0, size-1)
            data[i], data[j] = data[j], data[i]
        
        return data
    
    def generate_duplicate_heavy_data(self, size: int, unique_count: int = None) -> List[int]:
        """중복값이 많은 데이터 생성"""
        if unique_count is None:
            unique_count = max(1, size // 10)  # 전체의 10%만 고유값
        
        # 고유값 생성
        unique_values = [random.randint(-100000, 100000) for _ in range(unique_count)]
        
        # 각 고유값을 여러 번 복제하여 전체 크기 맞추기
        data = []
        for _ in range(size):
            data.append(random.choice(unique_values))
        
        random.shuffle(data)
        return data
    
    def generate_nearly_sorted_data(self, size: int, swap_percentage: float = 0.05) -> List[int]:
        """거의 정렬된 데이터 생성 (몇 개 원소만 위치가 바뀜)"""
        # 먼저 정렬된 데이터 생성
        data = self.generate_sorted_data(size)
        
        # 일부 원소들의 위치만 바꾸기
        swap_count = max(1, int(size * swap_percentage))
        
        for _ in range(swap_count):
            i = random.randint(0, size - 1)
            j = random.randint(max(0, i - 10), min(size - 1, i + 10))  # 가까운 위치와만 교환
            data[i], data[j] = data[j], data[i]
        
        return data
    
    def generate_data_by_pattern(self, pattern: DataPattern, size: int, **kwargs) -> List[int]:
        """패턴에 따라 데이터 생성"""
        if pattern == DataPattern.RANDOM:
            return self.generate_random_data(size, **kwargs)
        elif pattern == DataPattern.SORTED:
            return self.generate_sorted_data(size, **kwargs)
        elif pattern == DataPattern.REVERSE:
            return self.generate_reverse_data(size, **kwargs)
        elif pattern == DataPattern.PARTIAL_SORTED:
            return self.generate_partial_sorted_data(size, **kwargs)
        elif pattern == DataPattern.DUPLICATES:
            return self.generate_duplicate_heavy_data(size, **kwargs)
        elif pattern == DataPattern.NEARLY_SORTED:
            return self.generate_nearly_sorted_data(size, **kwargs)
        else:
            raise ValueError(f"Unknown pattern: {pattern}")
    
    def save_to_file(self, data: List[int], filename: str = "input.txt"):
        """데이터를 파일에 저장"""
        try:
            with open(filename, 'w') as f:
                # 첫 줄에 데이터 개수 저장
                f.write(f"{len(data)}\n")
                # 두 번째 줄에 모든 숫자를 공백으로 구분하여 저장
                f.write(' '.join(map(str, data)))
            
            print(f"✅ 테스트 데이터 생성 완료!")
            print(f"   파일: {filename}")
            print(f"   크기: {len(data):,}개")
            print(f"   시드: {self.seed}")
            print(f"   범위: {min(data)} ~ {max(data)}")
            print(f"   샘플: {data[:10]}{'...' if len(data) > 10 else ''}")
            
        except IOError as e:
            print(f"❌ 파일 저장 실패: {e}", file=sys.stderr)
            return False
        
        return True

def main():
    """메인 함수 - 명령줄 인터페이스"""
    parser = argparse.ArgumentParser(
        description="C++ 정렬 알고리즘 테스트용 랜덤 데이터 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python test_data_gen.py -s 100000                    # 10만개 랜덤 데이터
  python test_data_gen.py -s 50000 -p sorted           # 5만개 정렬된 데이터  
  python test_data_gen.py -s 10000 -p duplicates       # 1만개 중복 많은 데이터
  python test_data_gen.py -s 1000 --seed 12345         # 고정 시드로 재현 가능한 데이터
        """
    )
    
    parser.add_argument('-s', '--size', type=int, default=100000,
                        help='생성할 데이터 개수 (기본값: 100000)')
    
    parser.add_argument('-p', '--pattern', type=str, default='random',
                        choices=[p.value for p in DataPattern],
                        help='데이터 패턴 (기본값: random)')
    
    parser.add_argument('-o', '--output', type=str, default='input.txt',
                        help='출력 파일명 (기본값: input.txt)')
    
    parser.add_argument('--seed', type=int, default=None,
                        help='랜덤 시드 (재현 가능한 테스트용)')
    
    parser.add_argument('--min', type=int, default=-1000000,
                        help='최솟값 (기본값: -1000000)')
    
    parser.add_argument('--max', type=int, default=1000000,
                        help='최댓값 (기본값: 1000000)')
    
    args = parser.parse_args()
    
    # 데이터 크기 유효성 검사
    if args.size <= 0:
        print("❌ 데이터 크기는 1 이상이어야 합니다.", file=sys.stderr)
        return 1
    
    if args.size > 10**7:  # 1천만 개 제한
        print("❌ 데이터 크기가 너무 큽니다. (최대 10,000,000개)", file=sys.stderr)
        return 1
    
    # 값 범위 유효성 검사
    if args.min >= args.max:
        print("❌ 최솟값은 최댓값보다 작아야 합니다.", file=sys.stderr)
        return 1
    
    try:
        # 데이터 생성기 초기화
        generator = TestDataGenerator(seed=args.seed)
        
        # 패턴에 따라 데이터 생성
        pattern = DataPattern(args.pattern)
        
        print(f"📊 테스트 데이터 생성 중... (패턴: {pattern.value})")
        
        if pattern in [DataPattern.DUPLICATES]:
            # 중복 데이터의 경우 별도 파라미터
            data = generator.generate_data_by_pattern(pattern, args.size)
        else:
            data = generator.generate_data_by_pattern(pattern, args.size, 
                                                    min_val=args.min, max_val=args.max)
        
        # 파일에 저장
        success = generator.save_to_file(data, args.output)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())