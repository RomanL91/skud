async function fetch_data_in_server(pk_checkpoint, socketAddress, trFillFunc) {
  const preloadData = await fetch('http://' + window.location.host + '/api/v1/monitors/' + pk_checkpoint).then(function (response) {
    return response.json().then(async (thendata) => { return thendata })
  })
  table(pk_checkpoint, socketAddress, trFillFunc, preloadData)
}


function table(pk_checkpoint, socketAddress, trFillFunc, preloadData) {
  /**
   * Рендерим таблицу, заполняя строки с помощью переданной функции
   */
  preloadData = preloadData.sort((a, b) => a.time_created > b.time_created ? 1 : -1);

  const renderTable = () => {
    const tableBody = document.querySelector("tbody");
    while (tableBody.firstChild) {
      tableBody.removeChild(tableBody.firstChild);
    }
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = tableData.slice().reverse().slice(start, end);
    let index_i = true
    paginatedData.forEach((row) => {
      const gen_row = trFillFunc(row, index_i)
      index_i = false
      tableBody.append(gen_row);
    });
  };

  // Функция для отображения количества сотрудников на территории
  const renderCounter = (count) => {
    const counter = document.getElementById('perimeter_counter')
    counter.innerText = count;
  };


  /**
   * Рендерим пагинацию для таблицы
   */
  const renderPagination = () => {
    const clearPagination = () => {
      /** Удаляем и очищаем лисенеры старой пагинации */
      while (paginationContainer.firstChild) {
        paginationContainer.removeChild(paginationContainer.firstChild);
      }
    };

    /** Добавляем кнопку перехода на следующую страницу */
    const addFirstButton = () => {
      const firstButton = document.createElement("button");
      firstButton.textContent = "<<";
      firstButton.disabled = currentPage === 1;
      firstButton.addEventListener("click", () => {
        currentPage = 1;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(firstButton);
    };

    /** Добавляем кнопку перехода на предыдущую страницу */
    const addPrevButton = () => {
      const prevButton = document.createElement("button");
      prevButton.textContent = "<";
      prevButton.disabled = currentPage === 1;
      prevButton.addEventListener("click", () => {
        currentPage -= 1;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(prevButton);
    };

    /** Добавляем кнопку перехода на номер страницы и скрытие страниц, если их слишком много */
    const addPages = () => {
      // Добавляем кнопку перехода на номер страницы
      let startPage = 1;
      let endPage = totalPages;
      if (totalPages > 5) {
        if (currentPage < 4) {
          endPage = 5;
        } else if (currentPage > totalPages - 3) {
          startPage = totalPages - 4;
        } else {
          startPage = currentPage - 2;
          endPage = currentPage + 2;
        }
      }
      for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement("button");
        pageButton.textContent = i;
        pageButton.disabled = i === currentPage;
        pageButton.addEventListener("click", () => {
          currentPage = i;
          renderTable();
          renderPagination();
        });
        paginationContainer.appendChild(pageButton);
      }

      // Добавляем логику перехода на скрытые номера страниц, если больше 5 страниц
      if (totalPages > 5) {
        if (currentPage > 3) {
          const prevPagesButton = document.createElement("button");
          prevPagesButton.textContent = "...";
          prevPagesButton.addEventListener("click", () => {
            currentPage = startPage - 1;
            renderTable();
            renderPagination();
          });
          paginationContainer.insertBefore(
            prevPagesButton,
            paginationContainer.childNodes[2]
          );
        }
        if (currentPage < totalPages - 2) {
          const nextPagesButton = document.createElement("button");
          nextPagesButton.textContent = "...";
          nextPagesButton.addEventListener("click", () => {
            currentPage = endPage + 1;
            renderTable();
            renderPagination();
          });
          paginationContainer.appendChild(nextPagesButton);
        }
      }
    };

    /**Добавляем кнопку перехода на следующую страницу */
    const addNextButton = () => {
      const nextButton = document.createElement("button");
      nextButton.textContent = ">";
      nextButton.disabled = currentPage === totalPages;
      nextButton.addEventListener("click", () => {
        currentPage += 1;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(nextButton);
    };

    /**Добавляем кнопку перехода на последнюю страницу */
    const addLastButton = () => {
      const lastButton = document.createElement("button");
      lastButton.textContent = ">>";
      lastButton.disabled = currentPage === totalPages;
      lastButton.addEventListener("click", () => {
        currentPage = totalPages;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(lastButton);
    };
    clearPagination();
    addFirstButton();
    addPrevButton();
    addPages();
    addNextButton();
    addLastButton();
  };


  /** Устанавливаем связь по сокету */
  const connect = (pk_checkpoint) => {
    let ws = new WebSocket(socketAddress);
    //При получении сообщения
    ws.addEventListener("message", (event) => {

      const newData = JSON.parse(event.data);
      console.log('-----newData', newData)
      if(pk_checkpoint===newData.event.controller.id)
      {
        tableData.push(newData);

        // Вызываем функция для отображения счетчика передавая в нее число которое лети по WS
        renderCounter(newData.event.perimeter_counter)
  
        totalPages = Math.ceil(tableData.length / rowsPerPage);
        if (currentPage > totalPages) {
          currentPage = totalPages;
        }
        const status_mode = document.getElementById('status_mode');
        if (newData.event.granted_reason == 'Без проверки биометрии') {
          status_mode.innerText = "Однофакторный"
        } else {
          status_mode.innerText = "Двухфакторный"
        }
        renderTable();
        renderPagination();
      }
    });

    // При потере коннекта
    ws.addEventListener("close", function (event) {
      console.log(
        "Socket is closed. Reconnect will be attempted in 1 second.",
        event.reason
      );
      alert('Потеряно соединение с главным сервером!!! Свяжитсь с поддержкой.')
      setTimeout(function () {
        connect();
      }, 1000);
    });
  };

  let tableData = preloadData

  tableData = tableData?.length ? tableData : [];

  let currentPage = 1;
  let rowsPerPage = 20;
  let totalPages = Math.ceil(tableData.length / rowsPerPage);

  const paginationContainer = document.querySelector(".pagination");

  renderTable();
  renderPagination();
  connect(pk_checkpoint);

}


// Функция открытия модального окна со списком персонала находящегося на территории
const loadPeopleInPerimeter = async (pk_checkpoint) => {

  // Получаем элемент содержания модального ока
  const modalContent = document.getElementById('modalBody');
  const newItem = document.createElement('p');


  // Загрузка данных с БД (список сотрудников и номеров их ключей)
  const data = await fetch(`http://${window.location.host}/api/v1/perimetr/${pk_checkpoint}`)
    .then(response => response.json())
    .then(response => {
      return response[0].perimeter_data;
    })
  // Преобразование объекта данны в массив имён сотрудников
  const peopleInTerritoryArr = Object.values(data);

  modalContent.innerHTML = "";
  peopleInTerritoryArr.map(el => {
    modalContent.innerHTML += `<li>${el}</li>`;
  })
}


const peopleInTerritoryModal = document.getElementById('myModal');
const perimeter_counter_container = document.getElementById('perimeter_counter_container');


peopleInTerritoryModal.addEventListener('shown.bs.modal', () => {
  perimeter_counter_container.click()
});
