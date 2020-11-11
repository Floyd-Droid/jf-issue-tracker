$(document).ready(function () {
  $('table.table').DataTable();

  // Ensure current user selects a user before assigning or unassigning to a project.
  $('#project-assign-btn, #project-unassign-btn').click(function () {
    num_checked = $("input[type=checkbox]:checked").length
    if (!num_checked) {
      alert('Please select at least one user.');
      return false;
    }
  });
});