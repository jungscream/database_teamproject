// 더보기 버튼
function toggleMore() {
  const moreFilters = document.getElementById('moreFilters');
  moreFilters.classList.toggle('hidden');
}

window.addEventListener('DOMContentLoaded', async () => {

  const res = await fetch('http://localhost:5050/api/movies');
  const movies = await res.json();
 
  const tbody = document.querySelector('#movieTable tbody');
  movies.forEach(movie => {
    const row = `
      <tr>
      <td>${movie.movie_nm}</td>
      <td>${movie.movie_nm_eng}</td>
      <td>${movie.movie_id}</td>
      <td>${movie.open_year}</td>
      <td>${movie.nation}</td>
      <td>${movie.type}</td>
      <td>${movie.genre}</td>
      <td>${movie.status}</td>
      <td>${movie.director}</td>
      <td>${movie.producer}</td>
      </tr>
    `;
    tbody.insertAdjacentHTML('beforeend', row);
  });

  // 총 결과 수 출력 
  let totalCount = movies.length;
  document.getElementById('resultCount').innerText = `총 ${totalCount}건의 검색`;

  // 페이징
function pagination() {
  var req_num_row = 10;
  var $tr = jQuery('tbody tr');
  var total_num_row = $tr.length;
  var num_pages = Math.ceil(total_num_row / req_num_row);

  let currentGroup = 1;
  const group_size = 10;

  const renderPagination = () => {
    jQuery('.pagination').empty();
    const totalGroups = Math.ceil(num_pages / group_size);
    const startPage = (currentGroup - 1) * group_size + 1;
    const endPage = Math.min(startPage + group_size - 1, num_pages);

    jQuery('.pagination').append(`<li><a class="first">First</a></li>`);
    jQuery('.pagination').append(`<li><a class="prev">Previous</a></li>`);

    for (let i = startPage; i <= endPage; i++) {
      jQuery('.pagination').append(`<li><a class="pagination-link">${i}</a></li>`);
    }

    jQuery('.pagination').append(`<li><a class="next">Next</a></li>`);
    jQuery('.pagination').append(`<li><a class="last">Last</a></li>`);

    jQuery('.pagination li:nth-child(3)').addClass("active"); // 첫 페이지 강조
    showPage(startPage);

    // 버튼 활성/비활성 처리
    jQuery('.first, .prev, .next, .last').parent().removeClass('disabled');

    if (currentGroup === 1) {
      jQuery('.first, .prev').parent().addClass('disabled');
    }
    if (currentGroup === totalGroups) {
      jQuery('.next, .last').parent().addClass('disabled');
    }
  };

  const showPage = (page) => {
    $tr.hide();
    const start = (page - 1) * req_num_row;
    for (let i = 0; i < req_num_row; i++) {
      $tr.eq(start + i).show();
    }
  };

  // 페이지 번호 클릭
  jQuery(document).on('click', '.pagination-link', function (e) {
    e.preventDefault();
    const page = parseInt(jQuery(this).text());
    jQuery('.pagination li').removeClass("active");
    jQuery(this).parent().addClass("active");
    showPage(page);
  });

  // 그룹 이동
  jQuery(document).on('click', '.prev', function (e) {
    e.preventDefault();
    if (currentGroup > 1) {
      currentGroup--;
      renderPagination();
    }
  });

  jQuery(document).on('click', '.next', function (e) {
    e.preventDefault();
    const totalGroups = Math.ceil(num_pages / group_size);
    if (currentGroup < totalGroups) {
      currentGroup++;
      renderPagination();
    }
  });

  // 처음 / 마지막 버튼
  jQuery(document).on('click', '.first', function (e) {
    e.preventDefault();
    currentGroup = 1;
    renderPagination();
  });

  jQuery(document).on('click', '.last', function (e) {
    e.preventDefault();
    currentGroup = Math.ceil(num_pages / group_size);
    renderPagination();
  });

  renderPagination();
}

 // 검색 버튼 눌렀을때
  document.querySelector('.search-btn').addEventListener('click', async () => {
    const movieNm = document.querySelector('#movieNameInput').value; // 영화명
    const director = document.querySelector('#directorInput').value; // 감독명
    const openYearInput1 = document.querySelector('#openYearInput1').value; // 제작연도 ~
    const openYearInput2 = document.querySelector('#openYearInput2').value; // ~ 제작연도
    const statusInput = document.querySelector('#statusInput').value; // 상태
    const typeInput = document.querySelector('#typeInput').value; // 유형
    const genreInput = document.querySelector('#genreInput').value; // 장르
    const nationInput = document.querySelector('#nationInput').value; // 국적
    const bossNationInput = document.querySelector('#bossNationInput').value; // 대표국적

    // 테이블 초기화
    const tbody = document.querySelector('#movieTable tbody');
    tbody.innerHTML = '';

    // 서버로 입력값 보내줌
    const params = new URLSearchParams();
    if (movieNm) params.append('movie_nm', movieNm);
    if (director) params.append('director', director);
    if (openYearInput1) params.append('open_year1', openYearInput1);
    if (openYearInput2) params.append('open_year2', openYearInput2);
    if (statusInput) params.append('status', statusInput);
    if (typeInput) params.append('type', typeInput);
    if (genreInput) params.append('genre', genreInput);
    if (nationInput) params.append('nation', nationInput);
    if (bossNationInput) params.append('bossNation', bossNationInput);

    try {
      const res = await fetch(`http://localhost:5050/api/search?${params.toString()}`);
      const data = await res.json();
      data.forEach(movie => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${movie.movie_nm}</td>
          <td>${movie.movie_nm_eng}</td>
          <td>${movie.movie_id}</td>
          <td>${movie.open_year}</td>
          <td>${movie.nation}</td>
          <td>${movie.type}</td>
          <td>${movie.genre}</td>
          <td>${movie.status}</td>
          <td>${movie.director}</td>
          <td>${movie.producer}</td>
        `;
        tbody.appendChild(row);
      });

    // 결과수 출력
    let totalCount = data.length;
    document.getElementById('resultCount').innerText = `총 ${totalCount}건의 검색`;

    pagination();

    } catch (err) {
      console.error("검색 실패:", err);
    }
  });

  // 초기화 버튼 눌렀을때
  const resetBtn = document.querySelector('.reset-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      document.querySelector('#movieNameInput').value = '';
      document.querySelector('#directorInput').value = '';
      document.querySelector('#openYearInput1').value = '';
      document.querySelector('#openYearInput2').value = '';
      document.querySelector('#statusInput').value = '';
      document.querySelector('#typeInput').value = '';
      document.querySelector('#genreInput').value = '';
      document.querySelector('#nationInput').value = '';
      document.querySelector('#bossNationInput').value = '';
    });
  } else {
    console.warn(".reset-btn 요소 못 찾음");
  }

  // 인덱싱
  document.querySelectorAll('.indexing-list a').forEach(el => {
    el.addEventListener('click', async (e) => {
      e.preventDefault();
      const index = e.target.getAttribute('data-index');
  
      const res = await fetch(`http://localhost:5050/api/indexing?index=${index}`);
      const data = await res.json();
  
      const tbody = document.querySelector('#movieTable tbody');
      tbody.innerHTML = '';
      data.forEach(movie => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${movie.movie_nm}</td>
          <td>${movie.movie_nm_eng}</td>
          <td>${movie.movie_id}</td>
          <td>${movie.open_year}</td>
          <td>${movie.nation}</td>
          <td>${movie.type}</td>
          <td>${movie.genre}</td>
          <td>${movie.status}</td>
          <td>${movie.director}</td>
          <td>${movie.producer}</td>
        `;
        tbody.appendChild(row);
      });
      let totalCount = data.length;
      document.getElementById('resultCount').innerText = `총 ${totalCount}건의 검색`;
      pagination();
    });
  });

  document.getElementById('sortSelect').addEventListener('change', async (e) => {
    const sortKey = e.target.value;
    const tbody = document.querySelector('#movieTable tbody');
    tbody.innerHTML = '';
  
    const res = await fetch(`http://localhost:5050/api/search?sort=${sortKey}`);
    const data = await res.json();
  
    data.forEach(movie => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${movie.movie_nm}</td>
        <td>${movie.movie_nm_eng}</td>
        <td>${movie.movie_id}</td>
        <td>${movie.open_year}</td>
        <td>${movie.nation}</td>
        <td>${movie.type}</td>
        <td>${movie.genre}</td>
        <td>${movie.status}</td>
        <td>${movie.director}</td>
        <td>${movie.producer}</td>
      `;
      tbody.appendChild(row);
    });
    let totalCount = data.length;
    document.getElementById('resultCount').innerText = `총 ${totalCount}건의 검색`;
    pagination();
  });

  // 페이징 
  jQuery(document).ready(function () {
    pagination();
  });

});