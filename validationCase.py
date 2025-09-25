#!/usr/bin/env python3
"""
정렬 결과 검증기
C++ 정렬 알고리즘의 출력 결과를 검증하고 분석합니다.
"""

import sys
import argparse
from typing import List, Tuple, Optional
from collections import Counter
import time

class ValidationResult:
    """검증 결과를 담는 클래스"""
    
    def __init__(self):
        self.success = True
        self.errors = []
        self.warnings = []
        self.stats = {}
    
    def add_error(self, message: str):
        """에러 추가"""
        self.success = False
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """경고 추가"""
        self.warnings.append(message)
    
    def add_stat(self, key: str, value):
        """통계 정보 추가"""
        self.stats[key] = value

class SortingValidator:
    """정렬 결과 검증 클래스"""
    
    def __init__(self, input_file: str = "input.txt", output_file: str = "output.txt"):
        self.input_file = input_file
        self.output_file = output_file
        self.original_data = None
        self.output_lines = None
        self.parsed_results = None
    
    def load_input_data(self) -> ValidationResult:
        """입력 데이터 로드"""
        result = ValidationResult()
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    result.add_error(f"입력 파일 '{self.input_file}'이 비어있습니다.")
                    return result
                
                # 공백으로 구분된 정수들을 파싱
                try:
                    self.original_data = [int(x) for x in content.split()]
                    result.add_stat("input_size", len(self.original_data))
                    result.add_stat("input_min", min(self.original_data))
                    result.add_stat("input_max", max(self.original_data))
                    result.add_stat("input_duplicates", len(self.original_data) - len(set(self.original_data)))
                    
                except ValueError as e:
                    result.add_error(f"입력 파일에 잘못된 정수가 포함되어 있습니다: {e}")
                    return result
                
        except FileNotFoundError:
            result.add_error(f"입력 파일 '{self.input_file}'을 찾을 수 없습니다.")
        except IOError as e:
            result.add_error(f"입력 파일을 읽는 중 오류가 발생했습니다: {e}")
        
        return result
    
    def load_output_data(self) -> ValidationResult:
        """출력 데이터 로드"""
        result = ValidationResult()
        
        try:
            with open(self.output_file, 'rb') as f:
                content = f.read()
                
            # 바이너리로 읽어서 정확한 줄바꿈 분석
            content_str = content.decode('utf-8')
            
            # 줄바꿈으로 분리 (마지막 줄바꿈 고려)
            self.output_lines = content_str.split('\n')
            
            # 마지막 줄이 빈 문자열이면 제거 (마지막에 줄바꿈이 있었다는 의미)
            if self.output_lines and self.output_lines[-1] == '':
                result.add_warning("마지막 줄 끝에 불필요한 줄바꿈이 있습니다.")
                self.output_lines.pop()
            
            result.add_stat("output_lines", len(self.output_lines))
            
        except FileNotFoundError:
            result.add_error(f"출력 파일 '{self.output_file}'을 찾을 수 없습니다.")
        except IOError as e:
            result.add_error(f"출력 파일을 읽는 중 오류가 발생했습니다: {e}")
        except UnicodeDecodeError as e:
            result.add_error(f"출력 파일의 인코딩이 잘못되었습니다: {e}")
        
        return result
    
    def validate_output_format(self) -> ValidationResult:
        """출력 형식 검증"""
        result = ValidationResult()
        
        if self.output_lines is None:
            result.add_error("출력 데이터가 로드되지 않았습니다.")
            return result
        
        # 정확히 3줄인지 확인
        if len(self.output_lines) != 3:
            result.add_error(f"출력 파일은 정확히 3줄이어야 합니다. (현재: {len(self.output_lines)}줄)")
            return result
        
        # 각 줄 형식 검증
        for i, line in enumerate(self.output_lines):
            algorithm_name = ["삽입 정렬", "병합 정렬", "병합-삽입 정렬"][i]
            
            # 줄 끝 공백 검사
            if line.endswith(' '):
                result.add_error(f"{algorithm_name} 결과 줄 끝에 불필요한 공백이 있습니다.")
            
            # 줄 시작 공백 검사
            if line.startswith(' '):
                result.add_error(f"{algorithm_name} 결과 줄 시작에 불필요한 공백이 있습니다.")
            
            # 연속된 공백 검사
            if '  ' in line:  # 두 개 이상의 연속 공백
                result.add_error(f"{algorithm_name} 결과에 연속된 공백이 있습니다.")
            
            # 빈 줄 검사
            if not line.strip():
                result.add_error(f"{algorithm_name} 결과가 빈 줄입니다.")
        
        return result
    
    def parse_output_results(self) -> ValidationResult:
        """출력 결과를 파싱하여 정수 배열로 변환"""
        result = ValidationResult()
        
        if self.output_lines is None:
            result.add_error("출력 데이터가 로드되지 않았습니다.")
            return result
        
        self.parsed_results = []
        algorithm_names = ["삽입 정렬", "병합 정렬", "병합-삽입 정렬"]
        
        for i, line in enumerate(self.output_lines):
            try:
                # 공백으로 분리하여 정수로 변환
                numbers = [int(x) for x in line.split()]
                self.parsed_results.append(numbers)
                result.add_stat(f"{algorithm_names[i]}_size", len(numbers))
                
            except ValueError as e:
                result.add_error(f"{algorithm_names[i]} 결과에 잘못된 정수가 포함되어 있습니다: {e}")
                self.parsed_results.append([])  # 빈 배열로 추가하여 인덱스 유지
        
        return result
    
    def validate_sorting_correctness(self) -> ValidationResult:
        """정렬 결과의 정확성 검증"""
        result = ValidationResult()
        
        if not self.original_data or not self.parsed_results:
            result.add_error("입력 또는 출력 데이터가 없습니다.")
            return result
        
        algorithm_names = ["삽입 정렬", "병합 정렬", "병합-삽입 정렬"]
        expected_sorted = sorted(self.original_data)
        
        for i, (name, sorted_result) in enumerate(zip(algorithm_names, self.parsed_results)):
            
            # 1. 크기 검증
            if len(sorted_result) != len(self.original_data):
                result.add_error(f"{name}: 결과 크기가 다릅니다. "
                               f"(입력: {len(self.original_data)}, 출력: {len(sorted_result)})")
                continue
            
            # 2. 원소 개수 검증 (Counter 사용)
            original_counter = Counter(self.original_data)
            result_counter = Counter(sorted_result)
            
            if original_counter != result_counter:
                result.add_error(f"{name}: 원소의 개수가 맞지 않습니다.")
                
                # 구체적인 차이점 찾기
                missing = original_counter - result_counter
                extra = result_counter - original_counter
                
                if missing:
                    result.add_error(f"  누락된 원소: {dict(missing)}")
                if extra:
                    result.add_error(f"  추가된 원소: {dict(extra)}")
                continue
            
            # 3. 정렬 순서 검증
            is_sorted_correctly = True
            for j in range(len(sorted_result) - 1):
                if sorted_result[j] > sorted_result[j + 1]:
                    result.add_error(f"{name}: 정렬이 올바르지 않습니다. "
                                   f"인덱스 {j}와 {j+1}에서 순서가 잘못됨 "
                                   f"({sorted_result[j]} > {sorted_result[j+1]})")
                    is_sorted_correctly = False
                    break
            
            # 4. 기댓값과 정확히 일치하는지 검증
            if is_sorted_correctly and sorted_result != expected_sorted:
                result.add_error(f"{name}: 정렬 결과가 기댓값과 다릅니다.")
            
            # 성공 시 통계 정보 추가
            if is_sorted_correctly and sorted_result == expected_sorted:
                result.add_stat(f"{name}_correct", True)
        
        return result
    
    def validate_algorithm_consistency(self) -> ValidationResult:
        """세 알고리즘 결과의 일치성 검증"""
        result = ValidationResult()
        
        if not self.parsed_results or len(self.parsed_results) != 3:
            result.add_error("세 개의 정렬 결과가 모두 없습니다.")
            return result
        
        insertion_result, merge_result, merge_insertion_result = self.parsed_results
        
        # 세 결과가 모두 동일한지 확인
        if insertion_result == merge_result == merge_insertion_result:
            result.add_stat("algorithms_consistent", True)
        else:
            result.add_error("세 알고리즘의 결과가 서로 다릅니다.")
            
            # 구체적인 차이점 분석
            if insertion_result != merge_result:
                result.add_error("삽입 정렬과 병합 정렬 결과가 다릅니다.")
            
            if insertion_result != merge_insertion_result:
                result.add_error("삽입 정렬과 병합-삽입 정렬 결과가 다릅니다.")
            
            if merge_result != merge_insertion_result:
                result.add_error("병합 정렬과 병합-삽입 정렬 결과가 다릅니다.")
        
        return result
    
    def analyze_data_characteristics(self) -> ValidationResult:
        """데이터 특성 분석"""
        result = ValidationResult()
        
        if not self.original_data:
            return result
        
        data = self.original_data
        size = len(data)
        
        # 기본 통계
        result.add_stat("data_size", size)
        result.add_stat("min_value", min(data))
        result.add_stat("max_value", max(data))
        result.add_stat("unique_count", len(set(data)))
        result.add_stat("duplicate_count", size - len(set(data)))
        
        # 정렬 상태 분석
        sorted_data = sorted(data)
        reverse_sorted_data = sorted(data, reverse=True)
        
        if data == sorted_data:
            result.add_stat("initial_state", "완전 정렬됨 (Best Case)")
        elif data == reverse_sorted_data:
            result.add_stat("initial_state", "완전 역순 (Worst Case)")
        else:
            # 부분적 정렬 정도 측정
            inversions = 0
            for i in range(size - 1):
                for j in range(i + 1, size):
                    if data[i] > data[j]:
                        inversions += 1
            
            max_inversions = size * (size - 1) // 2
            disorder_ratio = inversions / max_inversions if max_inversions > 0 else 0
            
            result.add_stat("initial_state", f"부분 정렬됨 (무질서도: {disorder_ratio:.2%})")
            result.add_stat("inversion_count", inversions)
        
        return result
    
    def run_full_validation(self) -> ValidationResult:
        """전체 검증 실행"""
        print("🔍 정렬 결과 검증을 시작합니다...")
        
        overall_result = ValidationResult()
        
        # 1. 입력 데이터 로드
        print("  📂 입력 데이터 로드 중...")
        input_result = self.load_input_data()
        overall_result.errors.extend(input_result.errors)
        overall_result.warnings.extend(input_result.warnings)
        overall_result.stats.update(input_result.stats)
        
        if not input_result.success:
            return overall_result
        
        # 2. 출력 데이터 로드
        print("  📄 출력 데이터 로드 중...")
        output_result = self.load_output_data()
        overall_result.errors.extend(output_result.errors)
        overall_result.warnings.extend(output_result.warnings)
        overall_result.stats.update(output_result.stats)
        
        if not output_result.success:
            return overall_result
        
        # 3. 출력 형식 검증
        print("  📝 출력 형식 검증 중...")
        format_result = self.validate_output_format()
        overall_result.errors.extend(format_result.errors)
        overall_result.warnings.extend(format_result.warnings)
        overall_result.stats.update(format_result.stats)
        
        # 4. 출력 결과 파싱
        print("  🔢 출력 결과 파싱 중...")
        parse_result = self.parse_output_results()
        overall_result.errors.extend(parse_result.errors)
        overall_result.warnings.extend(parse_result.warnings)
        overall_result.stats.update(parse_result.stats)
        
        if not parse_result.success:
            return overall_result
        
        # 5. 정렬 정확성 검증
        print("  ✅ 정렬 정확성 검증 중...")
        correctness_result = self.validate_sorting_correctness()
        overall_result.errors.extend(correctness_result.errors)
        overall_result.warnings.extend(correctness_result.warnings)
        overall_result.stats.update(correctness_result.stats)
        
        # 6. 알고리즘 일치성 검증
        print("  🔄 알고리즘 일치성 검증 중...")
        consistency_result = self.validate_algorithm_consistency()
        overall_result.errors.extend(consistency_result.errors)
        overall_result.warnings.extend(consistency_result.warnings)
        overall_result.stats.update(consistency_result.stats)
        
        # 7. 데이터 특성 분석
        print("  📊 데이터 특성 분석 중...")
        analysis_result = self.analyze_data_characteristics()
        overall_result.stats.update(analysis_result.stats)
        
        # 전체 성공 여부 결정
        overall_result.success = len(overall_result.errors) == 0
        
        return overall_result
    
    def print_validation_report(self, result: ValidationResult):
        """검증 결과 리포트 출력"""
        print("\n" + "="*70)
        if result.success:
            print("🎉 검증 성공! 모든 테스트를 통과했습니다.")
        else:
            print("❌ 검증 실패! 문제가 발견되었습니다.")
        print("="*70)
        
        # 에러 출력
        if result.errors:
            print("\n🚨 오류 목록:")
            for i, error in enumerate(result.errors, 1):
                print(f"  {i}. {error}")
        
        # 경고 출력
        if result.warnings:
            print("\n⚠️  경고 목록:")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")
        
        # 통계 정보 출력
        if result.stats:
            print("\n📊 통계 정보:")
            
            # 입력 데이터 정보
            if "data_size" in result.stats:
                print(f"  📂 입력 데이터:")
                print(f"     • 크기: {result.stats.get('data_size', 'N/A'):,}개")
                print(f"     • 범위: {result.stats.get('min_value', 'N/A')} ~ {result.stats.get('max_value', 'N/A')}")
                print(f"     • 고유값: {result.stats.get('unique_count', 'N/A'):,}개")
                print(f"     • 중복값: {result.stats.get('duplicate_count', 'N/A'):,}개")
                print(f"     • 초기 상태: {result.stats.get('initial_state', 'N/A')}")
            
            # 출력 형식 정보
            if "output_lines" in result.stats:
                print(f"  📄 출력 형식:")
                print(f"     • 줄 수: {result.stats.get('output_lines', 'N/A')}줄")
            
            # 알고리즘 성공 정보
            algorithms = ["삽입 정렬", "병합 정렬", "병합-삽입 정렬"]
            print(f"  ✅ 알고리즘 결과:")
            for algo in algorithms:
                key = f"{algo}_correct"
                status = "✓" if result.stats.get(key, False) else "✗"
                size = result.stats.get(f"{algo}_size", "N/A")
                print(f"     • {algo}: {status} (크기: {size:,}개)" if isinstance(size, int) else f"     • {algo}: {status} (크기: {size})")
            
            consistency = "✓" if result.stats.get("algorithms_consistent", False) else "✗"
            print(f"     • 일치성: {consistency}")
        
        print("\n" + "="*70)

def main():
    """메인 함수 - 명령줄 인터페이스"""
    parser = argparse.ArgumentParser(
        description="C++ 정렬 알고리즘 결과 검증기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python validator.py                           # 기본 파일 검증 (input.txt, output.txt)
  python validator.py -i data.txt -o result.txt # 사용자 지정 파일 검증
  python validator.py --quiet                   # 간단한 출력 모드
        """
    )
    
    parser.add_argument('-i', '--input', type=str, default='input.txt',
                        help='입력 파일명 (기본값: input.txt)')
    
    parser.add_argument('-o', '--output', type=str, default='output.txt',
                        help='출력 파일명 (기본값: output.txt)')
    
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='간단한 출력 모드 (성공/실패만 표시)')
    
    args = parser.parse_args()
    
    try:
        # 검증기 초기화
        validator = SortingValidator(args.input, args.output)
        
        # 전체 검증 실행
        start_time = time.time()
        result = validator.run_full_validation()
        end_time = time.time()
        
        # 결과 출력
        if args.quiet:
            if result.success:
                print("✅ PASS")
                return 0
            else:
                print("❌ FAIL")
                print(f"오류 {len(result.errors)}개 발견")
                return 1
        else:
            validator.print_validation_report(result)
            print(f"\n⏱️  검증 소요 시간: {end_time - start_time:.3f}초")
        
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())