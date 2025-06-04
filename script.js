// 더보기 버튼
function toggleMore() {
  const moreFilters = document.getElementById('moreFilters');
  moreFilters.classList.toggle('hidden');
}

window.addEventListener('DOMContentLoaded', async () => {
  const res = await fetch('http://localhost:5000/api/movies');
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
  jQuery(document).ready(function () {
    pagination();
  });

});